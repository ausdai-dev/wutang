# -*- coding: utf-8 -*-
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K_PATH = os.path.join(ROOT, "knowledge", "cards_mindset.json")
F_PATH = os.path.join(ROOT, "frontend", "assets", "cards_mindset.json")

NEW_CARDS = [
  {
    "card_id": "M-009",
    "card_type": "mindset",
    "title": "不配得感",
    "theme_tags": ["self_worth", "imposter", "anxiety"],
    "front_text": "遇到好事情的时候，我是在安心享受它，还是在提心吊胆地等待厄运？",
    "short_description": "这是一张用于自我反思的提示卡，不代表对你的判断。",
    "follow_up_question": "你是否总觉得当下的收获纯属侥幸，迟早会被人看穿？",
    "related_card_ids": ["W-001", "A-001"],
    "safety_boundary": "不得推断用户存在特定心理疾病；用户可随时跳过。",
    "status": "active",
    "version": "1.0"
  },
  {
    "card_id": "M-010",
    "card_type": "mindset",
    "title": "悬在半空的心",
    "theme_tags": ["grounding", "uncertainty", "safety"],
    "front_text": "我是在应对眼前的具体事情，还是在恐惧某种未知的崩塌？",
    "short_description": "这是一张用于自我反思的提示卡，不代表对你的判断。",
    "follow_up_question": "如果深呼吸回到脚踏实地的地面，此刻周围真正发生的危险是什么？",
    "related_card_ids": ["W-002", "A-002"],
    "safety_boundary": "不得推断用户存在特定心理疾病；用户可随时跳过。",
    "status": "active",
    "version": "1.0"
  },
  {
    "card_id": "M-011",
    "card_type": "mindset",
    "title": "被评价绑架",
    "theme_tags": ["criticism", "judgment", "authenticity"],
    "front_text": "别人对我的看法，真的必须成为我评价自己的唯一准绳吗？",
    "short_description": "这是一张用于自我反思的提示卡，不代表对你的判断。",
    "follow_up_question": "如果可以完全不向任何人证明自己，你最想做的是什么？",
    "related_card_ids": ["W-003", "A-003"],
    "safety_boundary": "不得推断用户存在特定心理疾病；用户可随时跳过。",
    "status": "active",
    "version": "1.0"
  },
  {
    "card_id": "M-012",
    "card_type": "mindset",
    "title": "假装情绪稳定",
    "theme_tags": ["suppression", "vulnerability", "emotional_health"],
    "front_text": "我是在真正释怀，还是在硬撑着不让自己流露委屈？",
    "short_description": "这是一张用于自我反思的提示卡，不代表对你的判断。",
    "follow_up_question": "如果卸下『懂事、成熟』的包袱，你最想对谁表达一句真实的委屈？",
    "related_card_ids": ["W-004", "A-004"],
    "safety_boundary": "不得推断用户存在特定心理疾病；用户可随时跳过。",
    "status": "active",
    "version": "1.0"
  },
  {
    "card_id": "M-013",
    "card_type": "mindset",
    "title": "无法休息的内疚",
    "theme_tags": ["guilt", "rest", "burnout"],
    "front_text": "休息本是生命的基础节律，我为什么会把它当成一种罪过？",
    "short_description": "这是一张用于自我反思的提示卡，不代表对你的判断。",
    "follow_up_question": "你是不是一停下来，就会产生强烈的落后恐慌与自责？",
    "related_card_ids": ["W-005", "A-005"],
    "safety_boundary": "不得推断用户存在特定心理疾病；用户可随时跳过。",
    "status": "active",
    "version": "1.0"
  },
  {
    "card_id": "M-014",
    "card_type": "mindset",
    "title": "难以说出需要",
    "theme_tags": ["boundaries", "hyper_independent", "relation"],
    "front_text": "求助真的代表软弱无能吗，还是我不习惯被他人接住？",
    "short_description": "这是一张用于自我反思的提示卡，不代表对你的判断。",
    "follow_up_question": "你习惯了照顾所有人的感受，那谁来照顾那个疲惫的你？",
    "related_card_ids": ["W-006", "A-006"],
    "safety_boundary": "不得推断用户存在特定心理疾病；用户可随时跳过。",
    "status": "active",
    "version": "1.0"
  },
  {
    "card_id": "M-015",
    "card_type": "mindset",
    "title": "进退两难的摇摆",
    "theme_tags": ["decision", "paralysis", "regret"],
    "front_text": "如果世上根本没有绝对完美的选项，我是在权衡利弊，还是在逃避遗憾？",
    "short_description": "这是一张用于自我反思的提示卡，不代表对你的判断。",
    "follow_up_question": "两种选择都会有未知的遗憾，哪一种遗憾是属于你自己的人生？",
    "related_card_ids": ["W-007", "A-007"],
    "safety_boundary": "不得推断用户存在特定心理疾病；用户可随时跳过。",
    "status": "active",
    "version": "1.0"
  },
  {
    "card_id": "M-016",
    "card_type": "mindset",
    "title": "不被理解的孤独",
    "theme_tags": ["isolation", "connection", "loneliness"],
    "front_text": "我渴望被真正看见，还是早早给自己贴上了『没人懂我』的封条？",
    "short_description": "这是一张用于自我反思的提示卡，不代表对你的判断。",
    "follow_up_question": "在这座喧嚣的城市里，是否有一个时刻，你觉得自己像一座孤岛？",
    "related_card_ids": ["W-008", "A-008"],
    "safety_boundary": "不得推断用户存在特定心理疾病；用户可随时跳过。",
    "status": "active",
    "version": "1.0"
  }
]

with open(K_PATH, "r", encoding="utf-8") as f:
    cards = json.load(f)

existing_ids = {c["card_id"] for c in cards}
added = 0
for nc in NEW_CARDS:
    if nc["card_id"] not in existing_ids:
        cards.append(nc)
        added += 1

print(f"Added {added} cards, total: {len(cards)}")

with open(K_PATH, "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

with open(F_PATH, "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print("[✓] cards_mindset.json 更新完毕")
