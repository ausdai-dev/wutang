# -*- coding: utf-8 -*-
"""登录用户长期记忆 API。"""
from typing import Literal

import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from backend.services.auth_service import get_current_user
from backend.services.memory_service import (
    MAX_MEMORY_CHARS,
    clear_memories,
    create_memory,
    delete_memory,
    list_memories,
    update_memory,
)


class PrivateMemoryRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def private_handler(request):
            try:
                return await handler(request)
            except RequestValidationError:
                return JSONResponse(
                    status_code=422,
                    content={
                        "code": "invalid_memory_request",
                        "message": "记忆请求格式或长度不符合要求，请检查后重试。",
                    },
                )

            except sqlite3.Error:
                return JSONResponse(status_code=503, content={
                    "code": "memory_unavailable", "message": "长期记忆存储暂不可用，请稍后重试。"
                })

        return private_handler


router = APIRouter(
    prefix="/api/memory",
    tags=["长期记忆"],
    route_class=PrivateMemoryRoute,
)


class MemoryWriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    content: str = Field(..., min_length=1, max_length=MAX_MEMORY_CHARS)
    confirmed: StrictBool = Field(..., description="必须由用户明确确认")
    source_type: Literal["manual", "suggestion"] = "manual"

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("content 不能为空")
        return value


class MemoryUpdateRequest(MemoryWriteRequest):
    pass


class ConfirmRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    confirmed: StrictBool = Field(..., description="必须由用户明确确认")


# 路由顺序保持清晰：集合 GET/POST/DELETE，再处理单项 PATCH/DELETE。
@router.get("")
async def get_memories(current_user: dict = Depends(get_current_user)):
    return {"status": "success", "memories": list_memories(current_user["id"])}


@router.post("")
async def add_memory(
    req: MemoryWriteRequest,
    current_user: dict = Depends(get_current_user),
):
    if req.confirmed is not True:
        raise HTTPException(status_code=400, detail="保存长期记忆前需要明确确认")
    memory = create_memory(current_user["id"], req.content, req.source_type)
    return {"status": "success", "memory": memory}


@router.delete("")
async def clear_memory(
    req: ConfirmRequest,
    current_user: dict = Depends(get_current_user),
):
    if req.confirmed is not True:
        raise HTTPException(status_code=400, detail="清空长期记忆前需要明确确认")
    deleted = clear_memories(current_user["id"])
    return {"status": "success", "deleted": deleted}


@router.patch("/{memory_id}")
async def edit_memory(
    memory_id: str,
    req: MemoryUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    if req.confirmed is not True:
        raise HTTPException(status_code=400, detail="编辑长期记忆前需要明确确认")
    memory = update_memory(current_user["id"], memory_id, req.content)
    if memory is None:
        raise HTTPException(status_code=404, detail="记忆不存在")
    return {"status": "success", "memory": memory}


@router.delete("/{memory_id}")
async def remove_memory(
    memory_id: str,
    req: ConfirmRequest,
    current_user: dict = Depends(get_current_user),
):
    if req.confirmed is not True:
        raise HTTPException(status_code=400, detail="删除长期记忆前需要明确确认")
    if not delete_memory(current_user["id"], memory_id):
        raise HTTPException(status_code=404, detail="记忆不存在")
    return {"status": "success", "deleted": 1}
