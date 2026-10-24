# -*- coding: utf-8 -*-
"""
悟堂 · 身份认证与权限服务 (Auth Service)
- 遵循 NIST/OWASP 工业规范，采用 PBKDF2-HMAC-SHA256 密码加盐散列
- 原生安全 RFC 7519 JWT 令牌生成与验签（HS256）
- 支持默认管理员账号 (admin / admin) 播种
"""
import base64
import hashlib
import hmac
import json
import secrets
import time
import os
import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from fastapi import HTTPException, Header, Depends
from backend.database import db_manager

def _load_secret_key() -> str:
    configured = os.getenv("AUTH_SECRET_KEY")
    if configured is not None:
        secret = configured.strip()
    else:
        # 本地密钥文件受 *.key 忽略规则保护；无可用存储时拒绝启动。
        secret_path = Path(__file__).resolve().parent.parent / "data" / "auth-secret.key"
        try:
            fd = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            secret = secret_path.read_text(encoding="utf-8").strip()
        else:
            secret = secrets.token_hex(48)
            with os.fdopen(fd, "w", encoding="utf-8") as secret_file:
                secret_file.write(secret)
        if os.name != "nt":
            secret_path.chmod(0o600)
    retired_key_hash = "d8906d066c1c705981d4d563c68590c9f7a5e5dd6c40e9886cda195e3bb86e9a"
    if hashlib.sha256(secret.encode("utf-8")).hexdigest() == retired_key_hash:
        raise RuntimeError("AUTH_SECRET_KEY 必须更换为未公开的随机密钥")
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("AUTH_SECRET_KEY 必须至少包含 32 字节随机密钥")
    return secret


JWT_SECRET_KEY = _load_secret_key()
JWT_EXPIRATION_SECONDS = 7 * 24 * 3600  # 7 天有效

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """生成或比对安全加盐散列 (PBKDF2-HMAC-SHA256, 100,000次迭代)"""
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    pwd_hash = base64.b64encode(key).decode("utf-8")
    return salt, pwd_hash

def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """恒定时间防时序攻击比对密码"""
    _, calculated_hash = hash_password(password, salt)
    return hmac.compare_digest(calculated_hash, expected_hash)

def _b64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64_url_decode(data: str) -> bytes:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", data):
        raise ValueError("凭据无效")
    return base64.b64decode(data + "=" * (-len(data) % 4), altchars=b"-_", validate=True)

def create_access_token(user: Dict[str, Any], expires_in: int = JWT_EXPIRATION_SECONDS) -> str:
    """生成标准 RFC 7519 HS256 JWT Token"""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": user["id"],
        "username": user.get("username"),
        "email": user.get("email"),
        "role": user.get("role", "user"),
        "daohao_nickname": user.get("daohao_nickname", "同修"),
        "iat": now,
        "exp": now + expires_in
    }

    header_b64 = _b64_url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64_url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_access_token(token: str) -> Dict[str, Any]:
    """验签并解析 JWT Token"""
    try:
        parts = token.strip().split(".")
        if len(parts) != 3:
            raise ValueError("Token 格式不合法")

        header_b64, payload_b64, sig_b64 = parts
        header = json.loads(_b64_url_decode(header_b64))
        if not isinstance(header, dict) or header.get("alg") != "HS256" or header.get("typ") != "JWT":
            raise ValueError("凭据无效")
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64_url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise ValueError("Token 签名无效")

        payload_bytes = _b64_url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        if not isinstance(payload, dict):
            raise ValueError("凭据无效")
        if type(payload.get("exp")) is not int or payload["exp"] <= int(time.time()):
            raise ValueError("凭据无效")
        if not isinstance(payload.get("sub"), str) or not payload["sub"].strip() or len(payload["sub"]) > 128:
            raise ValueError("凭据无效")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="身份凭据无效或已过期，请重新登录") from None

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """FastAPI 依赖注入：提取并验证当前登录用户"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供身份凭据，请先登录")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="凭证格式必须为: Bearer <token>")

    token = parts[1]
    payload = verify_access_token(token)
    user = db_manager.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在或已被注销")

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "daohao_nickname": user["daohao_nickname"],
        "preferred_track": user.get("preferred_track", "confucianism")
    }

# 初始化开机播种默认管理员
db_manager.seed_default_admin(hash_password)
