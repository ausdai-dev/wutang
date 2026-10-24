# -*- coding: utf-8 -*-
"""登录用户长期记忆的持久化与只读读取服务。"""
from contextlib import closing
from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

from backend.database import db_manager
from backend.services.auth_service import get_current_user

MAX_MEMORY_CHARS = 2000
MAX_MEMORY_ITEMS = 100
DEFAULT_READ_ITEMS = 20
DEFAULT_READ_TOKENS = 1200
MAX_READ_ITEMS = 100
MAX_READ_TOKENS = 4000


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_memory_table() -> None:
    """创建记忆表；数据库不可用时让异常向上传播，不伪造成功。"""
    with closing(db_manager.get_connection()) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                source_type TEXT NOT NULL DEFAULT 'manual',
                confirmed INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_user_memories_user_updated "
            "ON user_memories (user_id, updated_at DESC)"
        )
        conn.commit()


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "content": row["content"],
        "source_type": row["source_type"],
        "confirmed": bool(row["confirmed"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_memories(user_id: str) -> List[Dict[str, Any]]:
    with closing(db_manager.get_connection()) as conn, conn:
        rows = conn.execute(
            "SELECT id, content, source_type, confirmed, created_at, updated_at "
            "FROM user_memories WHERE user_id = ? AND confirmed = 1 ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
    return [_row_to_dict(row) for row in rows]


def create_memory(
    user_id: str,
    content: str,
    source_type: str = "manual",
) -> Dict[str, Any]:
    now = _utc_now()
    memory_id = str(uuid.uuid4())
    with closing(db_manager.get_connection()) as conn, conn:
        conn.execute("BEGIN IMMEDIATE")
        count = conn.execute(
            "SELECT COUNT(*) FROM user_memories WHERE user_id = ?", (user_id,)
        ).fetchone()[0]
        if count >= MAX_MEMORY_ITEMS:
            raise HTTPException(status_code=400, detail="长期记忆数量已达上限")
        conn.execute(
            "INSERT INTO user_memories "
            "(id, user_id, content, source_type, confirmed, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, 1, ?, ?)",
            (memory_id, user_id, content, source_type, now, now),
        )
        conn.commit()
    return {
        "id": memory_id,
        "content": content,
        "source_type": source_type,
        "confirmed": True,
        "created_at": now,
        "updated_at": now,
    }


def update_memory(user_id: str, memory_id: str, content: str) -> Optional[Dict[str, Any]]:
    now = _utc_now()
    with closing(db_manager.get_connection()) as conn, conn:
        cursor = conn.execute(
            "UPDATE user_memories SET content = ?, updated_at = ? "
            "WHERE id = ? AND user_id = ? AND confirmed = 1",
            (content, now, memory_id, user_id),
        )
        if cursor.rowcount == 0:
            return None
        row = conn.execute(
            "SELECT id, content, source_type, confirmed, created_at, updated_at "
            "FROM user_memories WHERE id = ? AND user_id = ?",
            (memory_id, user_id),
        ).fetchone()
        conn.commit()
    return _row_to_dict(row) if row else None


def delete_memory(user_id: str, memory_id: str) -> bool:
    with closing(db_manager.get_connection()) as conn, conn:
        cursor = conn.execute(
            "DELETE FROM user_memories WHERE id = ? AND user_id = ?",
            (memory_id, user_id),
        )
        conn.commit()
    return cursor.rowcount > 0


def clear_memories(user_id: str) -> int:
    with closing(db_manager.get_connection()) as conn, conn:
        cursor = conn.execute("DELETE FROM user_memories WHERE user_id = ?", (user_id,))
        conn.commit()
    return cursor.rowcount


def _user_from_authorization(authorization: Optional[str]) -> str:
    user = get_current_user(authorization)
    return user["id"]


def get_confirmed_memories_from_authorization(
    authorization: Optional[str],
    max_items: int = DEFAULT_READ_ITEMS,
    max_tokens: int = DEFAULT_READ_TOKENS,
) -> List[Dict[str, Any]]:
    """从 Authorization 验证用户并读取已确认记忆，供聊天编排只读调用。"""
    user_id = _user_from_authorization(authorization)
    item_limit = max(0, min(int(max_items), MAX_READ_ITEMS))
    token_limit = max(0, min(int(max_tokens), MAX_READ_TOKENS))
    if not item_limit or not token_limit:
        return []
    memories = list_memories(user_id)
    selected: List[Dict[str, Any]] = []
    used_tokens = 0
    for memory in memories:
        if not memory["confirmed"]:
            continue
        # UTF-8 字节数作为保守预算，避免中日韩字符被按英文四字一 token 低估。
        estimated_tokens = len(memory["content"].encode("utf-8"))
        if used_tokens + estimated_tokens > token_limit:
            break
        selected.append(memory)
        used_tokens += estimated_tokens
        if len(selected) >= item_limit:
            break
    return selected


async def aget_confirmed_memories_from_authorization(
    authorization: Optional[str],
    max_items: int = DEFAULT_READ_ITEMS,
    max_tokens: int = DEFAULT_READ_TOKENS,
) -> List[Dict[str, Any]]:
    return await run_in_threadpool(
        get_confirmed_memories_from_authorization, authorization, max_items, max_tokens
    )


init_memory_table()
