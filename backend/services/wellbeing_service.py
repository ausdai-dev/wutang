# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 心境健康与标准化自评服务 (Wellbeing Service)
严格恪守 PRD 3.0 第 4.4 / 10.7 / 18.9 节门禁铁律：
1. 确定性代码计分，绝对禁止 LLM 自由算分或修改常模。
2. 未获专业审核批准的量表一律强制处于 disabled_until_approved。
3. 区分自评与临床诊断，高危信号独立触发安全求助流程。
"""
import json
import uuid
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from backend.config import settings

class WellbeingService:
    def __init__(self):
        self.instruments: List[Dict[str, Any]] = []
        self.scoring_rules: Dict[str, Dict[str, Any]] = {}
        self.interpretation_copy: Dict[str, Dict[str, Any]] = {}
        self._load_wellbeing_data()

    def _load_wellbeing_data(self):
        knowledge_dir = settings.KNOWLEDGE_DIR
        wb_dir = knowledge_dir / "wellbeing"

        # 1. 加载量表注册表
        reg_file = wb_dir / "instrument_registry.json"
        if reg_file.exists():
            with open(reg_file, "r", encoding="utf-8") as f:
                self.instruments = json.load(f)

        # 2. 加载计分规则
        rules_dir = wb_dir / "scoring_rules"
        if rules_dir.exists():
            for rf in rules_dir.glob("*.json"):
                with open(rf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    inst_id = data.get("instrument_id")
                    if inst_id:
                        self.scoring_rules[inst_id] = data

        # 3. 加载专业解释文案
        copy_dir = wb_dir / "interpretation_copy"
        if copy_dir.exists():
            for cf in copy_dir.glob("*.json"):
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    inst_id = data.get("instrument_id")
                    if inst_id:
                        self.interpretation_copy[inst_id] = data

    def list_instruments(self) -> List[Dict[str, Any]]:
        """获取所有自评量表信息（含上线状态）"""
        return self.instruments

    def get_instrument(self, instrument_id: str) -> Optional[Dict[str, Any]]:
        for inst in self.instruments:
            if inst.get("instrument_id") == instrument_id:
                return inst
        return None

    def calculate_score(self, instrument_id: str, answers: List[int]) -> Dict[str, Any]:
        """
        确定性程序计分 (Deterministic Scoring)
        """
        inst = self.get_instrument(instrument_id)
        if not inst:
            return {
                "success": False,
                "error": "instrument_not_found",
                "message": f"未找到指定量表: {instrument_id}"
            }

        # 门禁铁律检查：若非 active，拒绝计分并提示
        if inst.get("launch_status") != "active":
            return {
                "success": False,
                "error": "disabled_until_approved",
                "message": f"量表《{inst.get('name')}》尚未完成专业临床与伦理审核，当前处于预览与等待开放状态，系统严禁生成未审核的自评分数。"
            }

        rules = self.scoring_rules.get(instrument_id)
        if not rules:
            return {
                "success": False,
                "error": "rules_missing",
                "message": f"量表 {instrument_id} 缺少已审核的计分规则。"
            }

        expected_count = len(inst.get("items", []))
        if len(answers) != expected_count:
            return {
                "success": False,
                "error": "invalid_answers_length",
                "message": f"题目数量不匹配：预期 {expected_count} 题，实际收到 {len(answers)} 题答案。"
            }

        # 针对 PSS-10 的确定性标准计分
        reverse_indices = [idx - 1 for idx in rules.get("reverse_items", [])]
        direct_indices = [idx - 1 for idx in rules.get("direct_items", [])]

        total_score = 0
        transformed_scores = []
        for i, val in enumerate(answers):
            val_clean = max(0, min(4, int(val)))
            if i in reverse_indices:
                score_item = 4 - val_clean
            else:
                score_item = val_clean
            transformed_scores.append(score_item)
            total_score += score_item

        # 匹配区间
        matched_range = None
        for r in rules.get("ranges", []):
            if r["min"] <= total_score <= r["max"]:
                matched_range = r
                break
        if not matched_range and rules.get("ranges"):
            matched_range = rules["ranges"][-1]

        level = matched_range.get("level", "moderate") if matched_range else "moderate"
        level_label = matched_range.get("label", "中度压力") if matched_range else "中度压力"

        # 提取专业文案
        copy_info = self.interpretation_copy.get(instrument_id, {})
        inter_map = copy_info.get("interpretations", {}).get(level, {})

        # 安全关怀拦截规则
        is_safety_flagged = False
        safety_message = ""
        # 题 10（第 10 项）选 3 或 4 且总分 >= 28
        item_10_raw = answers[9] if len(answers) >= 10 else 0
        if item_10_raw >= 3 and total_score >= 28:
            is_safety_flagged = True
            safety_message = "我们注意到你近期感到困难积聚过多且超出自我掌控。请一定先放慢节奏，关照自己的身心，必要时参考下方全国免费心理援助热线或寻求专业就医支持。"

        assessment_id = f"AS-{time.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"

        return {
            "success": True,
            "assessment_id": assessment_id,
            "instrument_id": instrument_id,
            "instrument_name": inst.get("name"),
            "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "total_score": total_score,
            "max_score": rules.get("max_score", 40),
            "level": level,
            "level_label": level_label,
            "summary": matched_range.get("summary", ""),
            "mindset_insight": inter_map.get("mindset_insight", ""),
            "oriental_wisdom_angle": inter_map.get("oriental_wisdom_angle", ""),
            "next_steps": inter_map.get("next_steps", []),
            "is_safety_flagged": is_safety_flagged,
            "safety_message": safety_message,
            "disclaimer": inst.get("disclaimer", "自评用于自我了解与进一步求助决策，不能当作疾病诊断或医疗处方。")
        }

wellbeing_service = WellbeingService()
