# -*- coding: utf-8 -*-
"""
悟堂 · 数据库管理中心 (SQLite 本地优先 / 支持 Render PostgreSQL 环境变量扩展)
- 零配置即开即用：默认在 backend/data/wutang.db 自动建表与持久化
- 包含用户账号表 (users)、会话与卡牌收藏记录
- 开机自检并自动播种默认主理人管理员账号 (admin / admin)
"""
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "wutang.db"

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """初始化数据表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 1. 用户表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                daohao_nickname TEXT DEFAULT '同修',
                preferred_track TEXT DEFAULT 'confucianism',
                created_at TEXT NOT NULL,
                last_login_at TEXT
            )
            """)

            # 2. 用户卡牌人生典藏表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_favorite_cards (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                card_type TEXT NOT NULL,
                card_id TEXT NOT NULL,
                card_name TEXT NOT NULL,
                series TEXT,
                core TEXT,
                question TEXT,
                image_png TEXT,
                saved_note TEXT,
                collected_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """)

            # 3. 用户心事日记表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_journals (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT,
                raw_content TEXT NOT NULL,
                structured_data TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """)

            conn.commit()

    def seed_default_admin(self, hash_func):
        """开机播种默认管理员/主理人账号 (admin / admin)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = 'admin' OR email = 'admin'")
            row = cursor.fetchone()
            if not row:
                salt, pwd_hash = hash_func("admin")
                user_id = str(uuid.uuid4())
                now = datetime.utcnow().isoformat()
                cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, salt, role, daohao_nickname, preferred_track, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    "admin",
                    "admin@wutang.com",
                    pwd_hash,
                    salt,
                    "admin",
                    "悟堂主理人",
                    "symposium",
                    now
                ))
                conn.commit()
                print("[db] Default admin account seeded: admin / admin (role: admin, daohao: 悟堂主理人)")

    # ---------------- 用户 CRUD 操作 ----------------

    def create_user(self, email: str, pwd_hash: str, salt: str, daohao: Optional[str] = None) -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        username = email.split("@")[0] if "@" in email else email
        nickname = (daohao.strip() if daohao else "") or f"{username}同修"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, salt, role, daohao_nickname, preferred_track, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                username,
                email,
                pwd_hash,
                salt,
                "user",
                nickname,
                "confucianism",
                now
            ))
            conn.commit()

        return {
            "id": user_id,
            "username": username,
            "email": email,
            "role": "user",
            "daohao_nickname": nickname,
            "created_at": now
        }

    def get_user_by_account(self, account: str) -> Optional[Dict[str, Any]]:
        """按用户名或邮箱查询用户（支持直接输入 admin 或邮箱登录）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT * FROM users WHERE email = ? OR username = ?
            """, (account, account))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_last_login(self, user_id: str):
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now, user_id))
            conn.commit()

    def update_profile(self, user_id: str, daohao: Optional[str], track: Optional[str]) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if daohao and track:
                cursor.execute("UPDATE users SET daohao_nickname = ?, preferred_track = ? WHERE id = ?", (daohao, track, user_id))
            elif daohao:
                cursor.execute("UPDATE users SET daohao_nickname = ? WHERE id = ?", (daohao, user_id))
            elif track:
                cursor.execute("UPDATE users SET preferred_track = ? WHERE id = ?", (track, user_id))
            conn.commit()
        return self.get_user_by_id(user_id)

db_manager = DatabaseManager()
