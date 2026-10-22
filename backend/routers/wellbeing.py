# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 心境健康与标准化自评路由
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.wellbeing_service import wellbeing_service
from backend.services.resource_service import resource_service
from backend.services.llm_service import llm_service

router = APIRouter(prefix="/api", tags=["心境健康"])

class ScoreRequest(BaseModel):
    instrument_id: str = Field(..., description="量表标识 (如 pss-10)")
    answers: List[int] = Field(..., description="每题得分数组 (0-4)")
    consent_to_record: bool = Field(False, description="用户是否同意将结果写入本地记录")

class ReferralRequest(BaseModel):
    main_complaint: str = Field(..., description="主要困扰与不适", max_length=500)
    duration: str = Field("约2周到1个月", description="持续时间")
    assessment_score: Optional[int] = Field(None, description="自评得分参考")
    target_specialist: str = Field("心理咨询师 / 综合医院心理科医师", description="期望面询方向")

@router.get("/wellbeing/instruments")
async def get_instruments():
    """获取所有自评量表定义与上线状态"""
    return {
        "success": True,
        "instruments": wellbeing_service.list_instruments()
    }

@router.post("/wellbeing/score")
async def calculate_score(req: ScoreRequest):
    """
    【确定性计分接口】根据经审核规则计算分值，严禁大模型算分幻觉
    """
    result = wellbeing_service.calculate_score(req.instrument_id, req.answers)
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("error"),
            "message": result.get("message")
        }
    return result

@router.get("/resources")
async def get_resources(region: Optional[str] = None, service_type: Optional[str] = None):
    """获取经核验的专业心理健康与危机干预服务资源"""
    items = resource_service.list_resources(region, service_type)
    return {
        "success": True,
        "total": len(items),
        "regions": resource_service.get_available_regions(),
        "resources": items
    }

@router.post("/referral/summary")
async def generate_referral_summary(req: ReferralRequest):
    """
    【授权转介摘要生成】生成面询沟通清单，不作临床诊断
    """
    summary = await llm_service.build_referral_summary(
        main_complaint=req.main_complaint,
        duration=req.duration,
        assessment_score=req.assessment_score,
        target_specialist=req.target_specialist
    )
    return {
        "success": True,
        "summary": summary
    }
