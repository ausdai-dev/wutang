# -*- coding: utf-8 -*-
"""
从原始 CSV 完整提取 96 张卡牌元数据（包含用户引导问题），
并更新 cards_96_catalog.json 与 cards_parsed.json
"""

import os
import csv
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "DOC", "悟堂_东方智慧卡牌96张生图提示词_因缘相惜版.csv")
CATALOG_PATH = os.path.join(ROOT, "frontend", "assets", "cards_96_catalog.json")
PARSED_PATH = os.path.join(ROOT, "DOC", "cards_parsed.json")

catalog = []
with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cid = row["编号"].strip()
        cname = row["卡牌名称"].strip()
        series = row["主题系列"].strip()
        core = row["核心寓意"].strip()
        scene = row["单卡画面提示词"].strip()
        question = row["用户引导问题"].strip()
        
        catalog.append({
            "card_id": f"WUTANG-CARD-{cid}",
            "num": cid,
            "name": cname,
            "series": series,
            "core": core,
            "question": question,
            "scene": scene,
            "image_png": f"assets/cards/images/{cid}_{cname}.png",
            "image_jpg": f"assets/cards/images/{cid}_{cname}.jpg",
            "aspect_ratio": "2:3",
            "resolution": "848x1264"
        })

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print(f"Updated {len(catalog)} cards with guide questions in {CATALOG_PATH}")
