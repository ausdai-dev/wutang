# -*- coding: utf-8 -*-
"""
悟堂 · 注册、登录与修道身份路由 (PRD 方案1 架构)
- 邮箱注册 + 两遍密码一致性校验
- 账号/邮箱登录，开机内置默认主理人 (admin / admin)
- JWT Token 签发与个人档案更新
"""
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from backend.database import db_manager
from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/api/auth", tags=["Auth 身份认证与修道档案"])

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

class RegisterRequest(BaseModel):
    email: str = Field(..., description="注册邮箱")
    password: str = Field(..., min_length=6, description="密码 (至少6位)")
    confirm_password: str = Field(..., description="确认密码 (两次输入必须完全一致)")
    daohao_nickname: Optional[str] = Field(None, description="个人专属修道道号 (如「归真子」)")

class LoginRequest(BaseModel):
    account: str = Field(..., description="登录账号 (邮箱 或 admin)")
    password: str = Field(..., description="登录密码")

class ProfileUpdateRequest(BaseModel):
    daohao_nickname: Optional[str] = Field(None, description="更新道号昵称")
    preferred_track: Optional[str] = Field(None, description="偏好流派: confucianism / daoism / buddhism / symposium")

@router.post("/register")
async def register(req: RegisterRequest):
    """
    用户注册：邮箱 + 两遍密码校验
    """
    email = req.email.strip().lower()
    
    # 1. 邮箱格式校验
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(status_code=400, detail="请输入格式合法的电子邮箱")

    # 2. 两遍密码一致性校验 (密码两遍校验)
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的密码不一致，请仔细核对")

    # 3. 密码复杂度校验
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于 6 位")

    # 4. 检查是否已被注册
    existing = db_manager.get_user_by_account(email)
    if existing:
        raise HTTPException(status_code=400, detail="该邮箱已被注册，请直接登录")

    # 5. 安全散列与入库
    salt, pwd_hash = hash_password(req.password)
    user = db_manager.create_user(email, pwd_hash, salt, daohao=req.daohao_nickname)

    # 6. 生成 Token 并返回
    token = create_access_token(user)
    return {
        "status": "success",
        "message": "注册成功，欢迎步入悟堂！",
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login")
async def login(req: LoginRequest):
    """
    用户登录：支持普通邮箱 或 管理员 admin 登录
    默认管理员账号: admin，默认密码: admin
    """
    account = req.account.strip()
    user = db_manager.get_user_by_account(account)

    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误，请重试")

    # 校验密码
    if not verify_password(req.password, user["salt"], user["password_hash"]):
        raise HTTPException(status_code=400, detail="账号或密码错误，请重试")

    # 更新最近登录时间
    db_manager.update_last_login(user["id"])

    user_info = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "daohao_nickname": user["daohao_nickname"],
        "preferred_track": user.get("preferred_track", "confucianism")
    }

    token = create_access_token(user_info)
    return {
        "status": "success",
        "message": f"欢迎归堂，{user_info['daohao_nickname']}！",
        "access_token": token,
        "token_type": "bearer",
        "user": user_info
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前登录用户的修道档案与权限信息"""
    return {
        "status": "success",
        "user": current_user
    }

@router.put("/profile")
async def update_profile(req: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    """更新修道道号或偏好流派"""
    updated = db_manager.update_profile(current_user["id"], req.daohao_nickname, req.preferred_track)
    return {
        "status": "success",
        "message": "修道档案已更新",
        "user": {
            "id": updated["id"],
            "username": updated["username"],
            "email": updated["email"],
            "role": updated["role"],
            "daohao_nickname": updated["daohao_nickname"],
            "preferred_track": updated.get("preferred_track", "confucianism")
        }
    }
