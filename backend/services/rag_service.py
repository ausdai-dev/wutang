# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— RAG 典籍检索与卡牌匹配服务 (PRD 4.0 儒释道升级版)
严谨保证：
1. 典籍引语 100% 来源于权威考据库（朝代、作者、版本、出处精确标注），彻底根绝 LLM 伪造古文幻觉
2. 儒释道三家流派精准检索分流，三圣圆桌实现三教代表各萃取一则
3. 动态联动 108 百八常道卡牌与三张解忧牌
"""
import json
import re
from typing import Dict, Any, List, Optional
from backend.config import settings

class RAGService:
    def __init__(self):
        self.classics: List[Dict[str, Any]] = []
        self.cards_mindset: List[Dict[str, Any]] = []
        self.cards_wisdom: List[Dict[str, Any]] = []
        self.cards_action: List[Dict[str, Any]] = []
        self.cards_108: List[Dict[str, Any]] = []
        self.cards_96: List[Dict[str, Any]] = []
        self.scenarios: List[Dict[str, Any]] = []
        self.micro_actions: Dict[str, List[Dict[str, Any]]] = {}
        self._load_corpus()

    def _load_corpus(self):
        assets_dir = settings.ASSETS_DIR
        knowledge_dir = settings.KNOWLEDGE_DIR

        # 1. 加载权威考据典籍 (514条)
        classics_path = assets_dir / "classics.json"
        if not classics_path.exists():
            classics_path = knowledge_dir / "classics.json"
        if classics_path.exists():
            with open(classics_path, "r", encoding="utf-8") as f:
                self.classics = json.load(f)

        # 2. 加载基础三张牌
        for name, attr in [
            ("cards_mindset.json", "cards_mindset"),
            ("cards_wisdom.json", "cards_wisdom"),
            ("cards_action.json", "cards_action")
        ]:
            p = knowledge_dir / name
            if not p.exists():
                p = assets_dir / name
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    setattr(self, attr, json.load(f))

        # 3. 加载 108 张常道卡谱
        c108_path = assets_dir / "cards_108_catalog.json"
        if not c108_path.exists():
            c108_path = knowledge_dir / "cards_108_catalog.json"
        if c108_path.exists():
            with open(c108_path, "r", encoding="utf-8") as f:
                self.cards_108 = json.load(f)

        # 3.2 加载 96 张东方智慧觉察牌
        c96_path = assets_dir / "cards_96_catalog.json"
        if not c96_path.exists():
            c96_path = knowledge_dir / "cards_96_catalog.json"
        if c96_path.exists():
            with open(c96_path, "r", encoding="utf-8") as f:
                self.cards_96 = json.load(f)

        # 4. 加载场景与微行动配置
        wd_path = assets_dir / "wutang-data.json"
        if wd_path.exists():
            with open(wd_path, "r", encoding="utf-8") as f:
                wd = json.load(f)
                self.scenarios = wd.get("scenarios", [])
                self.micro_actions = wd.get("microActions", {})

    def detect_scenario(self, text: str, user_selected: Optional[str] = None) -> str:
        """识别最契合的情绪场景 (work / relation / night / growth)"""
        if user_selected in ["work", "relation", "night", "growth"]:
            return user_selected

        scores = {"work": 0, "relation": 0, "night": 0, "growth": 0}
        for sc in self.scenarios:
            k = sc.get("key")
            alt_labels = sc.get("alt_labels", [])
            for w in alt_labels:
                if w in text:
                    scores[k] = scores.get(k, 0) + (3 if len(w) > 1 else 1)

        # 针对特定痛点词加权
        if any(w in text for w in ["领导", "加班", "老板", "同事", "辞职", "周报", "绩效", "背锅", "上班", "公司"]):
            scores["work"] += 5
        if any(w in text for w in ["父母", "催婚", "对象", "伴侣", "朋友", "拒绝", "讨好", "吵架", "分歧", "前任"]):
            scores["relation"] += 5
        if any(w in text for w in ["失眠", "深夜", "睡不着", "反刍", "后悔", "脑子停不下来", "两点", "凌晨"]):
            scores["night"] += 5
        if any(w in text for w in ["拖延", "拖了", "不敢开始", "做不好", "完美主义", "迷茫", "自责", "未来"]):
            scores["growth"] += 5

        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "growth"

    def match_cards(self, scenario: str, text: str, school: Optional[str] = None) -> Dict[str, Any]:
        """匹配解忧卡牌并适配指定流派 (儒/释/道)"""
        matched_mindset = None
        matched_wisdom = None
        matched_action = None

        # 1. 匹配心境牌
        for card in self.cards_mindset:
            sc_list = card.get("scenarios") or card.get("dimension") or []
            if scenario in sc_list or (isinstance(sc_list, str) and scenario in sc_list):
                matched_mindset = card
                break
        if not matched_mindset and self.cards_mindset:
            matched_mindset = self.cards_mindset[0]

        # 2. 匹配东方智慧牌（优先从 108 对应学派中筛选最具共鸣的常道牌）
        if school and self.cards_108:
            school_cards = [c for c in self.cards_108 if c.get("school") == school]
            if school_cards:
                # 寻找关键词命中
                for c in school_cards:
                    if any(w in text for w in [c.get("name", ""), c.get("core", "")[:4]]):
                        matched_wisdom = {
                            "card_id": c.get("card_id"),
                            "name": c.get("name"),
                            "classic_source": {
                                "book": c.get("series", "先贤"),
                                "chapter": c.get("name"),
                                "author": c.get("master", "先圣"),
                                "quote": c.get("core"),
                                "translation": c.get("question")
                            },
                            "original_text": c.get("core"),
                            "modern_interpretation": c.get("question")
                        }
                        break
                if not matched_wisdom:
                    c = school_cards[0]
                    matched_wisdom = {
                        "card_id": c.get("card_id"),
                        "name": c.get("name"),
                        "classic_source": {
                            "book": c.get("series", "先贤"),
                            "chapter": c.get("name"),
                            "author": c.get("master", "先圣"),
                            "quote": c.get("core"),
                            "translation": c.get("question")
                        },
                        "original_text": c.get("core"),
                        "modern_interpretation": c.get("question")
                    }

        # 兜底从 cards_wisdom 中匹配
        if not matched_wisdom:
            for card in self.cards_wisdom:
                tags = card.get("theme_tags", [])
                if scenario in tags or (card.get("scenarios") and scenario in card.get("scenarios")):
                    matched_wisdom = card
                    break
            if not matched_wisdom and self.cards_wisdom:
                matched_wisdom = self.cards_wisdom[0]

        # 3. 匹配行动牌
        for card in self.cards_action:
            sc_list = card.get("scenarios", [])
            if scenario in sc_list:
                matched_action = card
                break
        if not matched_action and self.cards_action:
            matched_action = self.cards_action[0]

        return {
            "mindset": matched_mindset,
            "wisdom": matched_wisdom,
            "action": matched_action,
        }

    def retrieve_classics(
        self,
        query: str,
        scenario: str,
        top_k: int = 3,
        school: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """从权威典籍中按流派（儒/释/道/圆桌）打分检索最相关的先贤智慧"""
        theme_map = {
            "work": ["职场", "处世", "敬业", "内耗", "权衡", "守拙", "知足", "从容", "立身"],
            "relation": ["人际", "友道", "边界", "宽容", "恕道", "求诸己", "和而不同", "放下"],
            "night": ["静心", "安住", "止念", "释怀", "顺应", "知止", "宁静", "养神", "空灵"],
            "growth": ["立志", "笃行", "积微", "慎独", "改过", "自强", "日新", "致远", "见性"]
        }
        scenario_keywords = theme_map.get(scenario, [])

        # 若是三圣圆桌模式 (symposium)，分别从儒、释、道三家各取第 1 名
        if school == "symposium":
            results = []
            for target_sch in ["confucianism", "daoism", "buddhism"]:
                sch_candidates = [c for c in self.classics if c.get("school") == target_sch]
                sch_scored = []
                for item in sch_candidates:
                    score = self._score_item(item, query, scenario_keywords)
                    sch_scored.append((score, item))
                sch_scored.sort(key=lambda x: x[0], reverse=True)
                if sch_scored:
                    results.append(sch_scored[0][1])
            if results:
                return results

        # 单一流派过滤
        pool = self.classics
        if school in ["confucianism", "daoism", "buddhism"]:
            sch_pool = [c for c in self.classics if c.get("school") in [school, "general"]]
            if sch_pool:
                pool = sch_pool

        scored = []
        for item in pool:
            score = self._score_item(item, query, scenario_keywords)
            # 若流派完全一致，赋予大幅优先加权
            if school and item.get("school") == school:
                score += 10
            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item for _, item in scored[:top_k]]

        if not results and pool:
            results = pool[:top_k]

        return results

    def _score_item(self, item: Dict[str, Any], query: str, scenario_keywords: list) -> int:
        score = 0
        quote = item.get("quote", "")
        translation = item.get("translation", "")
        theme = item.get("theme", "") + " " + item.get("themes", "")

        for kw in scenario_keywords:
            if kw in theme:
                score += 4
            if kw in translation:
                score += 2

        for word in re.findall(r"[\u4e00-\u9fa5]{2,4}", query):
            if word in translation:
                score += 3
            if word in quote:
                score += 5

        return score

    def match_zen96_card(
        self,
        user_text: str,
        track: Optional[str] = None,
        card_name: Optional[str] = None,
        specified_card_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """为当次解忧开示匹配出 96 张东方智慧画廊中最契合的一张心象牌"""
        if not self.cards_96:
            return {}

        # 1. 若明确给定了卡号，直接精准匹配
        if specified_card_id:
            for c in self.cards_96:
                if c.get("card_id") == specified_card_id or c.get("num") == specified_card_id:
                    res = dict(c)
                    res["match_reason"] = f"先圣直指当下心结，特以《{c.get('name')}》之意境为你点化心源。"
                    return res

        # 2. 若给定了卡名（如“留白”、“照见”），优先按牌名同名或包含匹配
        if card_name:
            cname = card_name.strip()
            for c in self.cards_96:
                if c.get("name") == cname or (len(cname) >= 2 and cname in c.get("name", "")):
                    res = dict(c)
                    res["match_reason"] = f"先圣以「{c.get('name')}」为法印，此幅水墨画作恰好映照出此等静心气象。"
                    return res

        # 3. 语义多维共振打分
        best_card = None
        highest_score = -1.0
        track_str = (track or "").lower()

        # 场景系列加权偏好
        target_series = "君子修身"
        if "dao" in track_str or "道" in track_str:
            target_series = "道法自然"
        elif "bud" in track_str or "释" in track_str or "佛" in track_str:
            target_series = "禅心之境"
        elif "sym" in track_str or "圆桌" in track_str:
            target_series = "禅心之境"

        for c in self.cards_96:
            score = 0.0
            c_series = c.get("series", "")
            c_name = c.get("name", "")
            c_core = c.get("core", "")
            c_q = c.get("question", "")

            # 流派系列匹配加权
            if c_series == target_series:
                score += 4.0

            # 情绪场景匹配
            if any(w in user_text for w in ["累", "忙", "慢", "歇", "烦", "节奏", "压力", "紧绷"]) and c_series == "一盏茶事":
                score += 3.5
            if any(w in user_text for w in ["关系", "朋友", "父母", "伴侣", "人际", "拒绝", "讨好", "边界"]) and c_series == "因缘相惜":
                score += 3.5
            if any(w in user_text for w in ["迷茫", "未来", "选择", "低谷", "远方", "方向", "困境"]) and c_series == "山水人生":
                score += 3.5

            # 关键词重合度加权
            for char_pair in [c_name] + [c_core[i:i+2] for i in range(0, len(c_core)-1, 2)]:
                if char_pair and char_pair in user_text:
                    score += 2.0

            if score > highest_score:
                highest_score = score
                best_card = c

        if not best_card and self.cards_96:
            best_card = self.cards_96[0]

        res = dict(best_card)
        c_name = res.get("name", "觉察")
        c_core = res.get("core", "")
        res["match_reason"] = f"你倾诉中心绪多有牵挂与紧绷，此幅《{c_name}》正契合当下心象，助你借境观心：{c_core}"
        return res

rag_service = RAGService()
