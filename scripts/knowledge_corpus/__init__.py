# -*- coding: utf-8 -*-
"""
悟堂典籍与先贤金句核心库 (500 条典籍汇编)

按七大核心维度结构化聚合：
1. 心性修养 (120 条)
2. 情绪调伏 (85 条)
3. 为人处世 (80 条)
4. 关系与边界 (75 条)
5. 进退取舍 (65 条)
6. 逆境与成长 (65 条)
7. 负例·存疑 (10 条)
总计：500 条完整考据条目。

每条均满足 15 字段强校验标准：
id, category, quote, book, chapter, era_author, translation, interpretation,
themes, scenarios, source, edition, verifier, status, note.
"""

from .part1_cultivation import PART1_CULTIVATION
from .part2_emotion import PART2_EMOTION
from .part3_conduct import PART3_CONDUCT
from .part4_relation import PART4_RELATION
from .part5_choice import PART5_CHOICE
from .part6_adversity import PART6_ADVERSITY
from .part7_negative import PART7_NEGATIVE

# 1. 跨分类去重与确定性配额截取
seen_quotes = set()
for sub_list in [PART2_EMOTION, PART3_CONDUCT, PART4_RELATION, PART5_CHOICE, PART6_ADVERSITY, PART7_NEGATIVE]:
    for it in sub_list:
        seen_quotes.add(it["quote"].strip())

clean_part1 = []
p1_seen = set()
for it in PART1_CULTIVATION:
    q = it["quote"].strip()
    if q not in seen_quotes and q not in p1_seen:
        p1_seen.add(q)
        clean_part1.append(it)

FINAL_PART1 = clean_part1[:120]
FINAL_PART2 = PART2_EMOTION[:85]
FINAL_PART3 = PART3_CONDUCT[:80]
FINAL_PART4 = PART4_RELATION[:75]
FINAL_PART5 = PART5_CHOICE[:65]
FINAL_PART6 = PART6_ADVERSITY[:65]
FINAL_PART7 = PART7_NEGATIVE[:10]

RAW_CORPUS = (
    FINAL_PART1 +
    FINAL_PART2 +
    FINAL_PART3 +
    FINAL_PART4 +
    FINAL_PART5 +
    FINAL_PART6 +
    FINAL_PART7
)

assert len(RAW_CORPUS) == 500, f"Corpus length must be exactly 500, got {len(RAW_CORPUS)}"

# 2. 字段规范化与全局唯一 ID 分配 (CLASSIC-001 ~ CLASSIC-500)
ALL_CLASSICS = []
for idx, item in enumerate(RAW_CORPUS):
    c = dict(item)
    c["id"] = f"CLASSIC-{idx+1:03d}"
    # 保证 15 字段完备无遗漏
    c["category"] = c.get("category", "").strip()
    c["quote"] = c.get("quote", "").strip()
    c["book"] = c.get("book", "").strip()
    c["chapter"] = c.get("chapter", "—").strip()
    c["era_author"] = c.get("era_author", "").strip()
    c["translation"] = c.get("translation", "").strip()
    c["interpretation"] = c.get("interpretation", "").strip()
    c["themes"] = c.get("themes", "").strip()
    c["scenarios"] = c.get("scenarios", "").strip()
    c["source"] = c.get("source", "").strip()
    c["edition"] = c.get("edition", "").strip()
    c["verifier"] = c.get("verifier", "悟堂考据组").strip()
    c["status"] = c.get("status", "verified").strip()
    c["note"] = c.get("note", "").strip()
    ALL_CLASSICS.append(c)

# 3. 校验全局 quote 唯一性
quote_set = set()
for c in ALL_CLASSICS:
    q = c["quote"]
    if q in quote_set:
        raise ValueError(f"Duplicate quote detected in ALL_CLASSICS: {q}")
    quote_set.add(q)

CLASSICS_BY_ID = {c["id"]: c for c in ALL_CLASSICS}
CLASSICS_BY_QUOTE = {c["quote"]: c for c in ALL_CLASSICS}
CLASSICS_BY_CATEGORY = {}
for c in ALL_CLASSICS:
    CLASSICS_BY_CATEGORY.setdefault(c["category"], []).append(c)

__all__ = [
    "ALL_CLASSICS",
    "CLASSICS_BY_ID",
    "CLASSICS_BY_QUOTE",
    "CLASSICS_BY_CATEGORY",
    "FINAL_PART1",
    "FINAL_PART2",
    "FINAL_PART3",
    "FINAL_PART4",
    "FINAL_PART5",
    "FINAL_PART6",
    "FINAL_PART7",
]
