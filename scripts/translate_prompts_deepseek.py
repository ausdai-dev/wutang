# -*- coding: utf-8 -*-
"""
Translate card scenes from Chinese to English prompts for Imagen/Diffusion models using DeepSeek.
Processes cards 25 to 96 in batches.
"""

import os
import json
import urllib.request
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_JSON = os.path.join(ROOT, "DOC", "cards_parsed.json")
ENG_JSON = os.path.join(ROOT, "DOC", "cards_english_prompts.json")

URL = "https://api.deepseek.com/chat/completions"
KEY = "sk-f4bd976cf746421895b782f5228caaf7"

with open(ENG_JSON, "r", encoding="utf-8") as f:
    prompts_data = json.load(f)

prompt_map = {p["id"]: p for p in prompts_data}

with open(SRC_JSON, "r", encoding="utf-8") as f:
    cards = json.load(f)

def translate_batch(batch):
    items_text = []
    for c in batch:
        items_text.append(f"ID {c['id']}: Name: {c['name']}, Series: {c['series']}\nScene: {c['scene']}")
    
    prompt = f"""You are an expert art director and translator specializing in classical Chinese painting (Song dynasty, ink wash, Gongbi) and AI image prompts (Imagen 3 / Midjourney).
Translate the following cards' visual scenes into poetic, vivid, precise English descriptions suitable for image generation prompts.

Requirements for each card:
1. Provide a concise English pinyin tag for image naming (e.g. "25_chong_zhi").
2. Provide a 2-3 sentence English description of the visual scene, specifying: the central subject, composition/perspective, mood, and color palette (e.g. antique paper beige, misty grey, pine green, muted cinnabar).
3. Do NOT include any text, letters, or seals in the scene.

Input cards:
{"---".join(items_text)}

Respond ONLY with a JSON array of objects with the following schema:
[
  {{
    "id": "25",
    "pinyin": "25_xxx",
    "scene_en": "...",
    "palette": "..."
  }},
  ...
]
"""
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a professional art translator. Output strict JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 3000
    }
    req = urllib.request.Request(URL, data=json.dumps(data).encode("utf-8"), headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KEY}"
    })
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                content = res["choices"][0]["message"]["content"].strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                parsed = json.loads(content.strip())
                return parsed
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return []

# Batch in chunks of 15
cards_to_translate = [c for c in cards if int(c["id"]) >= 25]
chunk_size = 15

for i in range(0, len(cards_to_translate), chunk_size):
    chunk = cards_to_translate[i:i+chunk_size]
    print(f"Translating chunk {chunk[0]['id']} to {chunk[-1]['id']}...")
    res = translate_batch(chunk)
    for item in res:
        cid = str(item["id"]).zfill(2)
        if cid in prompt_map:
            prompt_map[cid]["pinyin"] = item["pinyin"]
            prompt_map[cid]["prompt"] = (
                f"Chinese ink wash and Gongbi painting on antique Xuan paper, vertical 2:3 ratio. "
                f"{item['scene_en']} "
                f"Palette of {item['palette']}. "
                f"Clean composition, elegant negative space, masterwork quality, spiritual tranquility. "
                f"No text, no words, no characters, no seals, no signatures, no watermark."
            )
    time.sleep(1)

# Write back
with open(ENG_JSON, "w", encoding="utf-8") as f:
    json.dump(list(prompt_map.values()), f, ensure_ascii=False, indent=2)

print("All card prompts successfully translated and updated!")
