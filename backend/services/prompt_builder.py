# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— Prompt 编排器
将 brand_tone.md 品牌文风铁律与 RAG 检索上下文熔铸为规范的 System & User Prompt
"""
import json
from typing import Dict, Any, List

SYSTEM_PROMPT_TEMPLATE = """你是由「悟堂·东方解忧处」精心调教的解忧倾听者。
你的角色像一位读过很多书、经历过风浪但温和平视的老朋友——不端着、不说教、不灌廉价鸡汤。

【核心文风原则 (来自《悟堂品牌与文风手册》)】：
1. **先接住，再说话**：先真诚复述并接纳用户的感受与困境，不否定、不急于讲道理，更不要说「你想太多了」。
2. **绝对真实，严禁伪名言**：古人言论必须严格使用下方上下文检索提供的【典籍考据】，严禁编造任何看似古雅实则杜撰的假名言。
3. **留出口**：建议使用「可以试一试」「或许能」「今晚不妨」，严禁使用「你应该」「你必须」「你不能」。
4. **小而具体**：行动建议必须是一个「今晚 5 分钟、阻力极低、不用做重大决定」的微动作。
5. **严禁词汇**：绝对不得出现以下词语：「治愈」「治疗」「药方」「处方」「诊断」「专治」「心理急诊室」「保证改善」「你一定是因为」「你本质上」。

【必须输出的「四步解忧方」标准结构】：
请严格按照以下四个 Markdown 二级标题输出：

## 01 听见了
(40–90字：温和复述当事人的处境与真实情绪，接纳他的难处，让他感到被认真听见)

## 02 古人有云
(引用上下文中的典籍原文与出处，用亲切白话讲透它对当下心事的关照，60–120字)

## 03 试试这一招
(给出一个今晚 5 分钟内就能动手的低阻力微行动，写明行动名称与 2~3 个具体小动作)

## 04 读这一段
(20–50字：轻量导读书目与篇章，供心静之时自留翻阅)
"""

def build_user_prompt(user_text: str, scenario: str, matched_cards: Dict[str, Any], retrieved_classics: List[Dict[str, Any]]) -> str:
    """构建注入 RAG 考据事实的 User Prompt"""
    # 提取推荐智慧牌信息
    wisdom_card = matched_cards.get("wisdom") or {}
    ws_source = wisdom_card.get("classic_source", {})
    quote = ws_source.get("quote") or wisdom_card.get("original_text", "")
    book = ws_source.get("book") or wisdom_card.get("source_title", "")
    chapter = ws_source.get("chapter") or wisdom_card.get("source_section", "")
    author = ws_source.get("author", "先贤")
    interpretation = ws_source.get("translation") or wisdom_card.get("modern_interpretation", "")

    # 提取推荐行动牌信息
    action_card = matched_cards.get("action") or {}
    action_title = action_card.get("title", "今晚 5 分钟微行动")
    action_steps = action_card.get("steps", [])

    # 备选典籍参考
    classics_context = []
    for idx, c in enumerate(retrieved_classics, 1):
        classics_context.append(
            f"{idx}. 《{c.get('book','')}·{c.get('chapter','')}》（{c.get('era_author','')}）: "
            f"「{c.get('quote','')}」—— 释意：{c.get('translation','')}"
        )
    classics_str = "\n".join(classics_context) if classics_context else "暂无额外备选"

    prompt = f"""【当事人心事倾诉】：
<user_statement>
{user_text}
</user_statement>

【系统已识别场景】：{scenario}

【检索匹配到的权威先贤典籍与考据（请优先选用并保证真实出处）】：
- 主选经典：{book} · {chapter}（{author}）
- 原文：『{quote}』
- 白话旨要：{interpretation}
- 其他备选典籍：
{classics_str}

【推荐的微行动参考原型】：
- 标题：{action_title}
- 参考微步骤：{'；'.join(action_steps)}

请基于上述真实考据，为这位当事人写下充满同理心与东方智慧启发的「四步解忧方」。
"""
    return prompt
