# -*- coding: utf-8 -*-
"""
悟堂 · 东方解脱之道卡牌导出与打印服务路由
提供 300 DPI 实体卡牌正反面渲染与工业打印压缩包导出
"""
import io
import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel, Field

from backend.services.card_render_service import card_render_service

router = APIRouter(prefix="/api/card", tags=["卡牌打印与导出"])

class CardExportRequest(BaseModel):
    card_id: Optional[str] = Field("001", description="卡牌ID编号")
    card_number: Optional[str] = Field(None, description="全球专属卡号，如 WU-RU-KFZ-20261022-A89F")
    school: Optional[str] = Field("confucianism", description="流派: confucianism / daoism / buddhism / symposium")
    master: Optional[str] = Field("孔子", description="导师姓名")
    name: str = Field("明德", description="2字卡牌法门名称")
    aphorism: Optional[str] = Field("君子求诸己，万般皆因行未至。", description="核心定心偈金句")
    core: Optional[str] = Field(None, description="核心释义")
    english_mantra: Optional[str] = Field(None, description="英文定心真言")
    user_statement: Optional[str] = Field(None, description="当事人困扰脱敏描述")
    user_nickname: Optional[str] = Field("同修", description="求道者道号/昵称")
    lunar_date: Optional[str] = Field("丙午年 · 霜降", description="干支历法节令")
    classic_source: Optional[str] = Field(None, description="典籍出处，如《论语·卫灵公》（春秋·孔子）")
    quote: Optional[str] = Field(None, description="典籍原文引语")
    interpretation: Optional[str] = Field(None, description="白话真解")
    action_title: Optional[str] = Field(None, description="当下 5 分钟微功课标题")
    action_steps: Optional[List[str]] = Field(None, description="微功课具体步骤列表")
    scene: Optional[str] = Field(None, description="水墨意境描述")

@router.post("/render-front")
async def render_front(req: CardExportRequest):
    """渲染 300 DPI 卡牌正面 PNG"""
    try:
        data = req.dict()
        img = card_render_service.render_card_front(data)
        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(300, 300))
        return Response(content=buf.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"正面渲染失败: {str(e)}")

@router.post("/render-back")
async def render_back(req: CardExportRequest):
    """渲染 300 DPI 卡牌背面 PNG"""
    try:
        data = req.dict()
        img = card_render_service.render_card_back(data)
        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(300, 300))
        return Response(content=buf.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"背面渲染失败: {str(e)}")

@router.post("/export-print-pack")
async def export_print_pack(req: CardExportRequest):
    """一键打包导出 300 DPI 实体卡牌印刷 ZIP 文件（含正面、背面、烫金遮罩与下单说明）"""
    try:
        data = req.dict()
        zip_bytes = card_render_service.create_print_pack(data)
        import urllib.parse
        ascii_filename = f"WUTANG-CARD-{int(time.time())}.zip"
        encoded_filename = urllib.parse.quote(f"悟堂解脱卡-{data.get('name', 'CARD')}-{int(time.time())}.zip")
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=\"{ascii_filename}\"; filename*=UTF-8''{encoded_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"打包导出失败: {str(e)}")
