# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 工业化安全风控服务 (Risk Guardrails)
严格遵循 safety_rules.md 与 PRD 2.0 规范：
- 48 个高危绝对阻断词 (high_risk)
- 70 个边界转介复核词 (review)
- 12 组隐蔽危机句式正则 (riskPatterns)
"""
import re
import json
from typing import Dict, Any, List
from backend.config import settings

SAFETY_MSG_HIGH = (
    "你写下的这句话，我看到了，也很在意。\n\n"
    "我不能替你做判断，但我想认真告诉你三件事：\n"
    "1. 你现在承受的，可能已经超出一个人独自扛的范围了。\n"
    "2. 这种时候，找真人聊一聊会比找我更有用——一个你信得过的人，或者当地的心理援助热线 / 急诊。\n"
    "3. 如果此刻有具体的危险，请先离开可能伤害到自己的地方，或立刻联系身边能马上到你身边的人。\n\n"
    "【全国 24 小时心理危机免费热线】\n"
    "• 全国希望 24 小时热线：400-161-9995\n"
    "• 北京心理危机干预中心：010-82951332\n\n"
    "你的感受是真实的，也值得被认真对待。请给自己一个机会，先找人陪一陪你。"
)

SAFETY_MSG_REVIEW = (
    "这件事，悟堂可能需要先守住边界。\n\n"
    "你提到的内容，涉及到临床医疗用药、精神专科诊断、未成年人关照或超验预测等范畴。\n"
    "悟堂是一个日常情绪整理与东方传统文化启发的温和工具，不具备医疗诊断、处方开具或心理治疗资质。\n\n"
    "为了更稳妥地照护好你，建议向正规医院临床心理科/精神科医师、持有国家资质的心理咨询师或身边的长辈寻求专业协助。"
)

class RiskService:
    def __init__(self):
        self.risk_high: List[str] = []
        self.risk_review: List[str] = []
        self.risk_patterns: List[re.Pattern] = []
        self._load_safety_lexicon()

    def _load_safety_lexicon(self):
        data_path = settings.ASSETS_DIR / "wutang-data.json"
        if data_path.exists():
            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.risk_high = data.get("riskHigh", [])
                self.risk_review = data.get("riskReview", [])
                patterns_raw = data.get("riskPatterns", [])
                for p in patterns_raw:
                    try:
                        self.risk_patterns.append(re.compile(p, re.IGNORECASE))
                    except re.error:
                        pass
            except Exception as e:
                print(f"[!] 加载安全词库警告: {e}")

        # 兜底绝对高危核心词
        fallback_high = ["自杀", "自尽", "轻生", "跳楼", "割腕", "喝农药", "不想活了", "了结生命", "绝望一死"]
        for w in fallback_high:
            if w not in self.risk_high:
                self.risk_high.append(w)

    def evaluate(self, text: str) -> Dict[str, Any]:
        """
        多轨安全风控评估
        返回:
          level: 'high_risk' | 'review' | 'normal'
          is_safe: bool
          message: 安全回应文本（若命中高危或复核）
          triggered: 命中的词或模式
        """
        if not text:
            return {"level": "normal", "is_safe": True, "message": "", "triggered": []}

        # 1. 第一轨：绝对高危关键词阻断 (high_risk)
        hit_high = [w for w in self.risk_high if w in text]
        if hit_high:
            return {
                "level": "high_risk",
                "is_safe": False,
                "message": SAFETY_MSG_HIGH,
                "triggered": hit_high,
            }

        # 2. 第二轨：隐蔽句式正则匹配 (high_risk)
        hit_patterns = []
        for pat in self.risk_patterns:
            if pat.search(text):
                hit_patterns.append(pat.pattern)
        if hit_patterns:
            return {
                "level": "high_risk",
                "is_safe": False,
                "message": SAFETY_MSG_HIGH,
                "triggered": hit_patterns,
            }

        # 3. 第三轨：医疗/精神/未成年人/玄学边界转介 (review)
        hit_review = [w for w in self.risk_review if w in text]
        if hit_review:
            return {
                "level": "review",
                "is_safe": False,
                "message": SAFETY_MSG_REVIEW,
                "triggered": hit_review,
            }

        # 4. 第四轨：正常日常情绪整理
        return {
            "level": "normal",
            "is_safe": True,
            "message": "",
            "triggered": [],
        }

risk_service = RiskService()
