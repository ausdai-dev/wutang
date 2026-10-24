# -*- coding: utf-8 -*-
"""使用临时 SQLite 和真实 JWT 验证长期记忆边界。"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import json
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app import app
from backend.database import DatabaseManager
from backend.services import auth_service as auth
from backend.services import memory_service as service


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


class TestDatabaseManager(DatabaseManager):
    def get_connection(self):
        conn = sqlite3.connect(self.db_path, factory=ClosingConnection)
        conn.row_factory = sqlite3.Row
        return conn


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        manager = TestDatabaseManager(Path(self.temp.name) / "test.db")
        for target in ("backend.database.db_manager", "backend.services.auth_service.db_manager", "backend.services.memory_service.db_manager"):
            mock = patch(target, manager)
            mock.start()
            self.addCleanup(mock.stop)
        service.init_memory_table()
        self.users = [manager.create_user(f"user{i}@example.com", "unused-hash", "unused-salt") for i in range(2)]
        self.tokens = [auth.create_access_token(user) for user in self.users]
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def request(self, method, path="/api/memory", user=0, body=None):
        kwargs = {"headers": {"Authorization": "Bearer " + self.tokens[user]}} if user is not None else {}
        if body is not None:
            kwargs["json"] = body
        return self.client.request(method, path, **kwargs)

    def save(self, content="仅当前用户可见", user=0, **extra):
        return self.request("POST", user=user, body={"content": content, "confirmed": True, **extra})

    def items(self, user=0):
        return self.request("GET", user=user).json()["memories"]

    def test_requires_login_on_all_routes(self):
        for method, path, body in [("GET", "/api/memory", None), ("POST", "/api/memory", {"content": "x", "confirmed": True}), ("PATCH", "/api/memory/id", {"content": "x", "confirmed": True}), ("DELETE", "/api/memory/id", {"confirmed": True}), ("DELETE", "/api/memory", {"confirmed": True})]:
            with self.subTest(method=method, path=path):
                self.assertEqual(self.request(method, path, user=None, body=body).status_code, 401)

    def test_isolation_and_unauthorized_mutations(self):
        memory = self.save().json()["memory"]
        self.assertEqual(self.items(1), [])
        for method, body in [("PATCH", {"content": "越权", "confirmed": True}), ("DELETE", {"confirmed": True})]:
            response = self.request(method, "/api/memory/" + memory["id"], user=1, body=body)
            self.assertEqual(response.status_code, 404)
        self.assertEqual(self.items(), [memory])

    def test_confirmation_is_strict(self):
        for value in [False, None, 1, "true", "false"]:
            with self.subTest(value=value):
                response = self.save("私密测试语句", confirmed=value)
                self.assertIn(response.status_code, (400, 422))
                self.assertNotIn("私密测试语句", response.text)
        self.assertEqual(self.request("POST", body={"content": "private"}).status_code, 422)
        self.assertEqual(self.items(), [])

    def test_invalid_requests_never_echo_body(self):
        for data in [
            {"content": "x" * 2001, "confirmed": True},
            {"content": " ", "confirmed": True},
            {"content": "private", "confirmed": True, "user_id": "sensitive-owner"},
            {"content": "private", "confirmed": True, "inferred_label": "sensitive-label"},
            {"content": "private", "confirmed": True, "source_type": "model-inference"},
        ]:
            response = self.request("POST", body=data)
            self.assertEqual(response.status_code, 422)
            for marker in ("private", "xxx", "sensitive-owner", "inferred_label", "sensitive-label", "model-inference"):
                self.assertNotIn(marker, response.text)
        response = self.client.post("/api/memory", headers={"Authorization": "Bearer " + self.tokens[0], "Content-Type": "application/json"}, content='{"secret-private":')
        self.assertEqual(response.status_code, 422)
        self.assertNotIn("secret-private", response.text)

    def test_edit_metadata_and_clear_are_isolated(self):
        memory = self.save("原文", source_type="suggestion").json()["memory"]
        other = self.save("另一用户", user=1).json()["memory"]
        url = "/api/memory/" + memory["id"]
        for method, path, body in [("PATCH", url, {"content": "改写", "confirmed": False}), ("DELETE", url, {"confirmed": False}), ("DELETE", "/api/memory", {"confirmed": False})]:
            self.assertEqual(self.request(method, path, body=body).status_code, 400)
        updated = self.request("PATCH", url, body={"content": "更新内容", "confirmed": True}).json()["memory"]
        self.assertEqual(updated["created_at"], memory["created_at"])
        self.assertGreaterEqual(updated["updated_at"], memory["updated_at"])
        self.assertEqual(updated["source_type"], "suggestion")
        self.assertEqual(updated["content"], "更新内容")
        self.assertEqual(self.request("DELETE", body={"confirmed": True}).json()["deleted"], 1)
        self.assertEqual(self.items(), [])
        self.assertEqual(self.items(1), [other])

    def test_delete_and_item_limit(self):
        with patch.object(service, "MAX_MEMORY_ITEMS", 2):
            self.assertEqual(self.save("a").status_code, 200)
            self.assertEqual(self.save("b").status_code, 200)
            self.assertEqual(self.save("c").status_code, 400)
        memory_id = self.items()[0]["id"]
        self.assertEqual(self.request("DELETE", "/api/memory/" + memory_id, body={"confirmed": True}).status_code, 200)
        self.assertEqual(len(self.items()), 1)
        self.assertEqual(self.request("DELETE", "/api/memory/" + memory_id, body={"confirmed": True}).status_code, 404)

    def test_read_budget_async_and_isolation(self):
        self.save("中文记忆")
        authorization = "Bearer " + self.tokens[0]
        self.assertEqual(service.get_confirmed_memories_from_authorization(authorization, max_tokens=2), [])
        self.assertEqual(service.get_confirmed_memories_from_authorization("Bearer " + self.tokens[1]), [])
        self.assertEqual(len(asyncio.run(service.aget_confirmed_memories_from_authorization(authorization, max_items=1, max_tokens=12))), 1)
        self.assertEqual(service.get_confirmed_memories_from_authorization(authorization, max_items=0), [])
        with self.assertRaises(HTTPException) as exc:
            service.get_confirmed_memories_from_authorization(None)
        self.assertEqual(exc.exception.status_code, 401)

    def test_storage_error_is_not_success(self):
        with patch("backend.routers.memory.list_memories", side_effect=sqlite3.OperationalError("sensitive-storage-detail")):
            response = self.request("GET")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("sensitive-storage-detail", response.text)

    def test_actual_hundred_item_limit_and_restart_persistence(self):
        for index in range(100):
            service.create_memory(self.users[0]["id"], f"条目{index}")
        self.assertEqual(self.save("第101条").status_code, 400)
        self.assertEqual(self.save("用户二不受限", user=1).status_code, 200)
        service.init_memory_table()
        self.assertEqual(len(self.items()), 100)
        self.assertEqual(len(self.items(1)), 1)

    def test_unconfirmed_rows_not_returned(self):
        memory = self.save().json()["memory"]
        with service.db_manager.get_connection() as conn:
            conn.execute("UPDATE user_memories SET confirmed=0 WHERE id=?", (memory["id"],))
        self.assertEqual(self.items(), [])
        self.assertEqual(service.get_confirmed_memories_from_authorization("Bearer " + self.tokens[0]), [])

    def test_concurrent_limit(self):
        def save(_):
            try:
                service.create_memory(self.users[0]["id"], "并发记忆")
                return 200
            except HTTPException as exc:
                return exc.status_code
        with patch.object(service, "MAX_MEMORY_ITEMS", 1), ThreadPoolExecutor(max_workers=4) as pool:
            statuses = list(pool.map(save, range(4)))
        self.assertEqual(statuses.count(200), 1)
        self.assertEqual(statuses.count(400), 3)

    def signed_token(self, payload, header=None, secret=None):
        parts = [auth._b64_url_encode(json.dumps(item).encode()) for item in (header or {"alg": "HS256", "typ": "JWT"}, payload)]
        signature = hmac.new((secret or auth.JWT_SECRET_KEY).encode(), ".".join(parts).encode(), hashlib.sha256).digest()
        return ".".join([*parts, auth._b64_url_encode(signature)])

    def assert_token_rejected(self, token):
        response = self.client.get("/api/memory", headers={"Authorization": "Bearer " + token})
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("private", response.text)

    def test_old_public_key_forgery_rejected(self):
        self.assert_token_rejected(self.signed_token(auth.verify_access_token(self.tokens[0]), secret="wutang-eastern-wisdom-secret-key-2026-auth"))

    def test_strict_exp_sub_alg(self):
        for changes in [{"exp": None}, {"exp": "9999999999"}, {"exp": True}, {"exp": 0}, {"sub": None}, {"sub": ""}, {"sub": []}]:
            with self.subTest(changes=changes):
                self.assert_token_rejected(self.signed_token({"sub": "private", "exp": int(time.time()) + 3600, **changes}))
        for alg in ["none", "HS512", "RS256"]:
            self.assert_token_rejected(self.signed_token({"sub": "private", "exp": int(time.time()) + 3600}, {"alg": alg, "typ": "JWT"}))
        self.assert_token_rejected(self.signed_token({"sub": "private"}))
        self.assert_token_rejected("private-malformed")

    def test_local_secret_is_persistent_and_ignored(self):
        import os

        key_path = Path(auth.__file__).resolve().parent.parent / "data" / "auth-secret.key"
        if "AUTH_SECRET_KEY" not in os.environ:
            self.assertTrue(key_path.exists())
            self.assertEqual(auth._load_secret_key(), auth.JWT_SECRET_KEY)
            if os.name != "nt":
                self.assertEqual(key_path.stat().st_mode & 0o777, 0o600)
        self.assertIn("*.key", (Path(auth.__file__).resolve().parents[2] / ".gitignore").read_text(encoding="utf-8"))

    def test_secret_config(self):
        for secret in ["", "short", "wutang-eastern-wisdom-secret-key-2026-auth"]:
            with patch.dict("os.environ", {"AUTH_SECRET_KEY": secret}), self.assertRaises(RuntimeError):
                auth._load_secret_key()
        with patch.dict("os.environ", {"AUTH_SECRET_KEY": "a" * 48}):
            self.assertEqual(auth._load_secret_key(), "a" * 48)

    def test_xss_is_plain_json_and_no_body_logs(self):
        text = '<img src=x onerror="alert(1)">'
        with patch("builtins.print") as printed:
            response = self.save(text)
            self.assertEqual(self.items()[0]["content"], text)
        self.assertTrue(response.headers["content-type"].startswith("application/json"))
        self.assertFalse(printed.called)


if __name__ == "__main__":
    unittest.main()
