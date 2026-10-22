# -*- coding: utf-8 -*-
"""
生成《悟堂 · 东方智慧卡牌 19-96 张生图提示词手册.md》
包含目录、卡牌中文寓意、场景说明、英文可直接复制生图提示词，
方便用户在 Gemini Web / Imagen 3 中逐一复制生成。
"""

import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC_DIR = os.path.join(ROOT, "DOC")
PARSED_JSON = os.path.join(DOC_DIR, "cards_parsed.json")
ENG_JSON = os.path.join(DOC_DIR, "cards_english_prompts.json")
OUTPUT_MD = os.path.join(DOC_DIR, "悟堂_东方智慧卡牌19-96张生图提示词手册.md")

with open(PARSED_JSON, "r", encoding="utf-8") as f:
    cards = json.load(f)

with open(ENG_JSON, "r", encoding="utf-8") as f:
    prompts = json.load(f)

prompt_map = {p["id"]: p for p in prompts}

# Filter cards 19 to 96
cards_to_include = [c for c in cards if int(c["id"]) >= 19]

md_lines = []
md_lines.append("# 悟堂 · 东方智慧卡牌（第 19 ~ 96 张）生图提示词手册")
md_lines.append("")
md_lines.append("> **说明**：本手册专为在 **Gemini（Web / App / Imagen 3）** 中手动逐张生图精心排版。")
md_lines.append("> - **生图规格建议**：纵向 2:3 比例（848×1264 或 1024×1536），风格为宋画淡墨水墨纸本与工笔设色。")
md_lines.append("> - **使用方式**：点击各卡牌下方的 **【Gemini 英文生图提示词】** 复制代码块，直接发送给 Gemini 即可。英文提示词已针对底模严格强化了“无文字、无水印、宣纸肌理与宋画留白”约束。")
md_lines.append("> - **文件保存建议**：生成后可直接保存至项目的 `output/cards_images/{编号}_{卡牌名称}.png`（或 `.jpg`）。")
md_lines.append("")
md_lines.append("---")
md_lines.append("")
md_lines.append("## 快速导航目录")
md_lines.append("")

# Table of contents grouped by series
series_groups = {}
for c in cards_to_include:
    s = c["series"]
    if s not in series_groups:
        series_groups[s] = []
    series_groups[s].append(c)

for sname, clist in series_groups.items():
    md_lines.append(f"### 【{sname}】系列")
    items_md = []
    for c in clist:
        cid = c["id"]
        cname = c["name"]
        items_md.append(f"[{cid} {cname}](#card-{cid})")
    md_lines.append(" · ".join(items_md))
    md_lines.append("")

md_lines.append("---")
md_lines.append("")
md_lines.append("## 卡牌提示词正文清单")
md_lines.append("")

for c in cards_to_include:
    cid = c["id"]
    cname = c["name"]
    series = c["series"]
    core = c["core"]
    scene = c["scene"]
    
    pinfo = prompt_map.get(cid, {})
    eng_prompt = pinfo.get("prompt", "")
    pinyin = pinfo.get("pinyin", f"{cid}_{cname}")
    
    md_lines.append(f'<a id="card-{cid}"></a>')
    md_lines.append(f"### 卡牌 {cid} · {cname}（{series}）")
    md_lines.append("")
    md_lines.append(f"- **核心寓意**：{core}")
    md_lines.append(f"- **画面意境（中文）**：{scene}")
    md_lines.append(f"- **建议保存文件名**：`{cid}_{cname}.png`")
    md_lines.append("")
    md_lines.append("#### 【Gemini / Imagen 3 复制生图提示词】")
    md_lines.append("```text")
    md_lines.append(eng_prompt)
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

content = "\n".join(md_lines)

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully generated handbook with {len(cards_to_include)} cards at {OUTPUT_MD}")
