# -*- coding: utf-8 -*-
"""多轮文化角色聊天 API。"""
import json
from contextlib import aclosing
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sse_starlette.sse import EventSourceResponse

from backend.services.auth_service import get_current_user
from backend.services.chat_service import CHAT_PERSONAS, GROUP_SPEAKERS, MASTER_ALIASES, stream_chat

class PrivateChatRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def private_handler(request):
            try:
                return await handler(request)
            except RequestValidationError:
                # 不暴露 input、ctx、动态字段名或整个请求体。
                return JSONResponse(status_code=422, content={
                    "code": "invalid_chat_request", "message": "聊天请求格式或长度不符合要求，请检查后重试。"
                })

        return private_handler


router = APIRouter(prefix="/api/chat", tags=["聊天"], route_class=PrivateChatRoute)
MAX_HISTORY = 40
MAX_MESSAGE_CHARS = 2000
MAX_TOTAL_CHARS = 16000


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_MESSAGE_CHARS)
    speaker: Optional[str] = Field(default=None, max_length=32)

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, value):
        if not value.strip():
            raise ValueError("消息内容不能为空")
        return value.strip()


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    messages: list[ChatMessage] = Field(min_length=1, max_length=MAX_HISTORY)
    mode: Literal["group", "solo"] = "group"
    track: Optional[Literal["confucianism", "daoism", "buddhism", "symposium"]] = None
    master: Optional[str] = Field(default=None, max_length=32)
    target: Optional[str] = Field(default=None, max_length=32)
    round_limit: int = Field(default=2, ge=1, le=3)
    summary: Optional[str] = Field(default=None, max_length=3000)
    use_memory: bool = True

    @model_validator(mode="after")
    def validate_chat(self):
        if self.messages[-1].role != "user":
            raise ValueError("最后一条消息必须来自 user")
        if sum(len(message.content) for message in self.messages) > MAX_TOTAL_CHARS:
            raise ValueError("对话总长度不能超过 16000 字")
        if self.summary is not None:
            self.summary = self.summary.strip() or None
        for message in self.messages:
            if message.role == "user" and message.speaker is not None:
                raise ValueError("user 消息不能指定 speaker")
            if message.speaker is not None:
                message.speaker = MASTER_ALIASES.get(message.speaker, message.speaker)
                if message.speaker not in CHAT_PERSONAS:
                    raise ValueError("历史消息 speaker 不在允许名单中")
        if self.mode == "group" and self.master == "all":
            self.master = None
        if self.master is not None:
            self.master = MASTER_ALIASES.get(self.master, self.master)
            if self.master not in CHAT_PERSONAS:
                raise ValueError("master 不在允许名单中")
        if self.target is not None:
            self.target = MASTER_ALIASES.get(self.target, self.target)
            allowed = GROUP_SPEAKERS if self.mode == "group" else CHAT_PERSONAS
            if self.target not in allowed:
                raise ValueError("target 不在允许名单中")
        return self


def get_optional_user(authorization: Optional[str] = Header(None)):
    """未登录可聊天；提供凭证时必须通过服务端验签。"""
    if not authorization:
        return None
    return get_current_user(authorization)


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    authorization: Optional[str] = Header(None),
):
    async def events():
        async with aclosing(stream_chat(
            req, current_user=current_user, authorization=authorization
        )) as chat:
            async for event in chat:
                yield {"data": json.dumps(event, ensure_ascii=False)}

    return EventSourceResponse(
        events(),
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        ping=15,
    )
