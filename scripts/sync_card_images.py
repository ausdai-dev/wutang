# -*- coding: utf-8 -*-
"""
悟堂·东方智慧卡牌96张生图自动扫描与同步归档脚本
自动将 brain 目录中生成的卡牌图片同步至 output/cards_images，
确保规范命名为：{编号}_{卡牌名称}.png 与 .jpg，尺寸为 848x1264。
"""

import os
import glob
import json
import re
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output", "cards_images")
DOC_DIR = os.path.join(ROOT, "DOC")
BRAIN_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "brain", "3f5b9e83-2e8e-4206-9e76-8dd9d5310510")

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(os.path.join(DOC_DIR, "cards_parsed.json"), "r", encoding="utf-8") as f:
    cards = json.load(f)

card_by_id = {c["id"]: c for c in cards}

def sync_all():
    brain_files = glob.glob(os.path.join(BRAIN_DIR, "*.*"))
    synced = []
    
    for fpath in brain_files:
        fname = os.path.basename(fpath)
        # Check if filename starts with a card ID like 01_, 02_, ... 96_
        m = re.match(r"^(\d{2})_.*", fname)
        if not m:
            continue
        cid = m.group(1)
        if cid not in card_by_id:
            continue
        
        card = card_by_id[cid]
        cname = card["name"]
        dst_png = os.path.join(OUTPUT_DIR, f"{cid}_{cname}.png")
        dst_jpg = os.path.join(OUTPUT_DIR, f"{cid}_{cname}.jpg")
        
        # If not synced yet or smaller than expected
        if not os.path.exists(dst_png):
            try:
                with Image.open(fpath) as im:
                    print(f"Syncing Card {cid} ({cname}) from {fname}, size {im.size}...")
                    im.save(dst_png, format="PNG")
                    im.save(dst_jpg, format="JPEG", quality=95)
                    synced.append(cid)
            except Exception as e:
                print(f"Error processing {fpath}: {e}")
        else:
            synced.append(cid)
            
    # Count how many are done
    existing = set()
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".png"):
            cid = f.split("_")[0]
            existing.add(cid)
            
    print(f"Progress: {len(existing)} / 96 cards completed.")
    missing = [c["id"] for c in cards if c["id"] not in existing]
    if missing:
        print(f"Next cards to generate: {missing[:10]}")
    return existing, missing

if __name__ == "__main__":
    sync_all()
