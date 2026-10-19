# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 解忧路由中心
提供流式 SSE 生成接口、非流式结构化接口、卡牌匹配与系统状态监测
"""
import json
import time
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.config import settings
from backend.services.risk_service import risk_service
from backend.services.rag_service import rag_service
from backend.services.llm_service import llm_service
from backend.services.prompt_builder import SYSTEM_PROMPT_TEMPLATE, build_user_prompt

router = APIRouter(prefix="/api", tags=["解忧服务"])

class ReliefRequest(BaseModel):
    text: str = Field(..., description="当事人书写的心事或困扰文本", max_length=1000)
    scenario: Optional[str] = Field(None, description="预选场景: work/relation/night/growth")
    case_id: Optional[str] = Field(None, description="会话唯一编号，若无则自动生成")

@router.get("/health")
async def health_check():
    """健康监测与 AI 后台驱动状态"""
    return {
        "status": "healthy",
        "app": "悟堂·东方解忧处 AI 驱动引擎",
        "version": "2.0.0",
        "llm_configured": settings.is_llm_configured,
        "model": settings.LLM_MODEL,
        "base_url": settings.LLM_BASE_URL,
        "fallback_enabled": settings.ENABLE_FALLBACK_STREAM,
        "classics_count": len(rag_service.classics),
        "cards_count": {
            "mindset": len(rag_service.cards_mindset),
            "wisdom": len(rag_service.cards_wisdom),
            "action": len(rag_service.cards_action),
        }
    }

@router.post("/relief/stream")
async def relief_stream(req: ReliefRequest):
    """
    【核心流式接口】四步解忧方实时 SSE 响应
    - 结合前端打字机效果
    - 优先先发卡牌与元数据 (meta)，随后持续推流 Token (token)，最后完成 (done)
    """
    case_id = req.case_id or f"WUTANG-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    text = req.text.strip()

    # 1. 严格安全风控检测 (F-07 护栏)
    risk_res = risk_service.evaluate(text)

    async def sse_event_stream():
        # 若触发高危或复核，只输出安全关怀与转介提示，严禁输出普通卡牌与经典
        if not risk_res["is_safe"]:
            safety_meta = {
                "type": "safety",
                "case_id": case_id,
                "level": risk_res["level"],
                "triggered": risk_res["triggered"],
                "message": risk_res["message"]
            }
            yield f"data: {json.dumps(safety_meta, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            return

        # 2. 场景与知识库检索 RAG
        sc = rag_service.detect_scenario(text, req.scenario)
        cards = rag_service.match_cards(sc, text)
        classics = rag_service.retrieve_classics(text, sc, top_k=3)

        # 3. 首先推送卡牌元数据包，前端可立刻完成卡面翻转与呈现
        meta_payload = {
            "type": "meta",
            "case_id": case_id,
            "scenario": sc,
            "cards": cards,
            "classics": classics[:2]
        }
        yield f"data: {json.dumps(meta_payload, ensure_ascii=False)}\n\n"

        # 4. 流式调用 LLM 生成个性化「四步解忧方」
        async for chunk in llm_service.stream_relief(text, sc, cards, classics):
            yield chunk

    return StreamingResponse(
        sse_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/relief/generate")
async def relief_generate(req: ReliefRequest):
    """
    【非流式完整接口】适用于后台批处理、主理人工作台成文草稿生成或离线归档
    """
    case_id = req.case_id or f"WUTANG-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    text = req.text.strip()

    risk_res = risk_service.evaluate(text)
    if not risk_res["is_safe"]:
        return {
            "case_id": case_id,
            "status": "safety_intercepted",
            "risk": risk_res,
            "relief_text": risk_res["message"],
            "cards": None
        }

    sc = rag_service.detect_scenario(text, req.scenario)
    cards = rag_service.match_cards(sc, text)
    classics = rag_service.retrieve_classics(text, sc, top_k=3)

    # 聚合流式输出为完整结果
    chunks = []
    async for chunk in llm_service.stream_relief(text, sc, cards, classics):
        if chunk.startswith("data: "):
            try:
                data = json.loads(chunk[6:].strip())
                if data.get("type") == "token":
                    chunks.append(data.get("content", ""))
            except:
                pass

    full_markdown = "".join(chunks)
    parsed_steps = llm_service.parse_markdown_four_step(full_markdown)

    return {
        "case_id": case_id,
        "status": "success",
        "risk": risk_res,
        "scenario": sc,
        "cards": cards,
        "four_step_parsed": parsed_steps,
        "raw_markdown": full_markdown
    }
