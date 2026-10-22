# -*- coding: utf-8 -*-
"""
生成并维护卡牌生产任务队列
"""

import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output", "cards_images")
DOC_DIR = os.path.join(ROOT, "DOC")

with open(os.path.join(DOC_DIR, "cards_parsed.json"), "r", encoding="utf-8") as f:
    cards = json.load(f)

with open(os.path.join(DOC_DIR, "cards_english_prompts.json"), "r", encoding="utf-8") as f:
    prompts = json.load(f)

prompt_by_id = {p["id"]: p for p in prompts}

existing_ids = set()
for f in os.listdir(OUTPUT_DIR):
    if f.endswith(".png"):
        existing_ids.add(f.split("_")[0])

queue = []
for c in cards:
    cid = c["id"]
    is_done = cid in existing_ids
    pinfo = prompt_by_id.get(cid, {})
    queue.append({
        "id": cid,
        "series": c["series"],
        "name": c["name"],
        "status": "COMPLETED" if is_done else "PENDING",
        "pinyin": pinfo.get("pinyin", f"{cid}_card"),
        "prompt": pinfo.get("prompt", "")
    })

queue_path = os.path.join(ROOT, "output", "cards_queue.json")
with open(queue_path, "w", encoding="utf-8") as f:
    json.dump(queue, f, ensure_ascii=False, indent=2)

done_count = sum(1 for q in queue if q["status"] == "COMPLETED")
pending_count = len(queue) - done_count
print(f"Queue updated: {done_count} completed, {pending_count} pending.")
