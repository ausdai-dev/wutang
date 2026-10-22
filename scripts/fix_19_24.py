# -*- coding: utf-8 -*-
import urllib.request
import json
import os

URL = "https://api.deepseek.com/chat/completions"
KEY = "sk-f4bd976cf746421895b782f5228caaf7"

with open("DOC/cards_parsed.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

with open("DOC/cards_english_prompts.json", "r", encoding="utf-8") as f:
    prompts = json.load(f)

prompt_map = {p["id"]: p for p in prompts}

target_cards = [c for c in cards if 19 <= int(c["id"]) <= 24]
items = [f"ID {c['id']}: {c['name']} [{c['series']}]\nScene: {c['scene']}" for c in target_cards]
prompt_text = "Translate these exact visual scenes into poetic English for Imagen 3/Gemini. Return JSON array [{id, pinyin, scene_en, palette}]:\n\n" + "\n---\n".join(items)

req = urllib.request.Request(URL, data=json.dumps({
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": prompt_text}],
    "temperature": 0.3
}).encode("utf-8"), headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})

with urllib.request.urlopen(req, timeout=20) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    content = res["choices"][0]["message"]["content"].strip()
    if content.startswith("```json"): content = content[7:]
    if content.startswith("```"): content = content[3:]
    if content.endswith("```"): content = content[:-3]
    parsed_items = json.loads(content.strip())
    for item in parsed_items:
        cid = str(item["id"]).zfill(2)
        if cid in prompt_map:
            prompt_map[cid]["pinyin"] = item["pinyin"]
            prompt_map[cid]["prompt"] = (
                f"Chinese ink wash and Gongbi painting on antique Xuan paper, vertical 2:3 ratio. "
                f"{item['scene_en']} Palette of {item['palette']}. "
                f"Clean composition, elegant negative space, masterwork quality, spiritual tranquility. "
                f"No text, no words, no characters, no seals, no signatures, no watermark."
            )
            print(f"Updated card {cid}: {item['scene_en'][:60]}...")

with open("DOC/cards_english_prompts.json", "w", encoding="utf-8") as f:
    json.dump(list(prompt_map.values()), f, ensure_ascii=False, indent=2)

print("Done updating cards 19-24.")
