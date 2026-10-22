# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 个人成长、AI 日记与情境练习室路由
"""
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.config import settings
from backend.services.llm_service import llm_service

router = APIRouter(prefix="/api", tags=["成长与情境练习"])

class JournalOrganizeRequest(BaseModel):
    raw_text: str = Field(..., description="当事人撰写的零散心事倾诉或日记", max_length=2000)
    consent_to_save: bool = Field(False, description="用户明确授权保存至本地日记")

class PracticeChatRequest(BaseModel):
    scenario_id: str = Field(..., description="练习场景标识")
    scenario_title: str = Field("日常沟通练习", description="场景标题")
    ai_role: str = Field("对话对象", description="AI 扮演的角色身份")
    user_draft: str = Field(..., description="用户练习的回复文本", max_length=500)
    history: List[Dict[str, str]] = Field(default_factory=list, description="前序对话历史")

@router.post("/journal/organize")
async def organize_journal(req: JournalOrganizeRequest):
    """
    【AI 心事日记结构化提炼】
    提炼：事件客观事实、脑海想法、情绪体验、可能需要、下一步选择
    """
    structured = await llm_service.organize_journal(req.raw_text)
    return {
        "success": True,
        "structured_journal": structured
    }

@router.post("/practice/chat")
async def practice_chat(req: PracticeChatRequest):
    """
    【情境练习室互动对话】
    AI 角色扮演回复 + 4 维度非评判反馈 + 替代表达推荐
    """
    result = await llm_service.practice_dialogue(
        scenario_title=req.scenario_title,
        ai_role=req.ai_role,
        user_draft=req.user_draft,
        history=req.history
    )
    return {
        "success": True,
        "practice_result": result
    }

@router.get("/theme_packs")
async def get_theme_packs():
    """获取 6 大主题卡牌包定义 (PRD 3.0 Section 18.12)"""
    pack_file = settings.KNOWLEDGE_DIR / "theme_packs.json"
    packs = []
    if pack_file.exists():
        with open(pack_file, "r", encoding="utf-8") as f:
            packs = json.load(f)
    return {
        "success": True,
        "packs": packs
    }

@router.get("/scenarios/practice")
async def get_practice_scenarios():
    """获取 5 大情境练习室沟通场景 (PRD 3.0 Section 18.8)"""
    sc_file = settings.KNOWLEDGE_DIR / "practice_scenarios.json"
    scenarios = []
    if sc_file.exists():
        with open(sc_file, "r", encoding="utf-8") as f:
            scenarios = json.load(f)
    return {
        "success": True,
        "scenarios": scenarios
    }
