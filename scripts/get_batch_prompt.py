# -*- coding: utf-8 -*-
import sys
import json

with open("DOC/cards_english_prompts.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)

start_id = sys.argv[1] if len(sys.argv) > 1 else "04"
count = int(sys.argv[2]) if len(sys.argv) > 2 else 3

selected = []
for p in prompts:
    if int(p["id"]) >= int(start_id) and len(selected) < count:
        selected.append(p)

for s in selected:
    print(f"Card {s['id']} ({s['name']})")
    print(f"  ImageName: {s['pinyin']}")
    print(f"  Prompt: {s['prompt']}")
    print()
