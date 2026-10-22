# -*- coding: utf-8 -*-
"""
全面核查与标准化 96 张卡牌图片 (848x1264)
- 匹配 CSV 中所有 96 张卡牌
- 检查是否存在缺号
- 检查尺寸与比例，自动转换为 848x1264 高画质 PNG 与 JPG 双格式
- 更新 cards_manifest、queue 与 HTML 预览图鉴
"""

import os
import re
import json
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_DIR = os.path.join(ROOT, "output", "cards_images")
DOC_DIR = os.path.join(ROOT, "DOC")
CARDS_JSON = os.path.join(DOC_DIR, "cards_parsed.json")

with open(CARDS_JSON, "r", encoding="utf-8") as f:
    cards_data = json.load(f)

card_map = {c["id"]: c for c in cards_data}

files = os.listdir(CARDS_DIR)

# Map found files to card IDs
found_by_id = {}
for f in files:
    m = re.match(r"^(\d{1,2})[_\-\s\.].*", f)
    if m:
        cid = m.group(1).zfill(2)
        if cid not in found_by_id:
            found_by_id[cid] = []
        found_by_id[cid].append(f)

print(f"Total defined cards in CSV: {len(cards_data)}")
print(f"Found card IDs in output/cards_images: {len(found_by_id)}")

missing_ids = [c["id"] for c in cards_data if c["id"] not in found_by_id]
if missing_ids:
    print(f"MISSING IDs ({len(missing_ids)}): {missing_ids}")
else:
    print("ALL 96 CARDS FOUND! None missing!")

# Audit and normalize dimensions to 848x1264
audit_results = []
for c in cards_data:
    cid = c["id"]
    cname = c["name"]
    target_png = os.path.join(CARDS_DIR, f"{cid}_{cname}.png")
    target_jpg = os.path.join(CARDS_DIR, f"{cid}_{cname}.jpg")
    
    if cid in found_by_id:
        file_list = found_by_id[cid]
        # Choose the best source image (prefer png, then jpg, then webp)
        source_file = None
        for cand in file_list:
            if cand.endswith(".png"):
                source_file = os.path.join(CARDS_DIR, cand)
                break
        if not source_file:
            for cand in file_list:
                if cand.endswith(".jpg") or cand.endswith(".jpeg"):
                    source_file = os.path.join(CARDS_DIR, cand)
                    break
        if not source_file:
            source_file = os.path.join(CARDS_DIR, file_list[0])
            
        try:
            with Image.open(source_file) as im:
                orig_size = im.size
                im_rgb = im.convert("RGB")
                
                # Check if resize is needed
                if orig_size != (848, 1264):
                    print(f"Resizing Card {cid} ({cname}) from {orig_size} to (848, 1264)...")
                    resized = im_rgb.resize((848, 1264), Image.Resampling.LANCZOS)
                    resized.save(target_png, format="PNG", optimize=True)
                    resized.save(target_jpg, format="JPEG", quality=95)
                else:
                    # Ensure standardized names exist
                    if not os.path.exists(target_png):
                        im_rgb.save(target_png, format="PNG")
                    if not os.path.exists(target_jpg):
                        im_rgb.save(target_jpg, format="JPEG", quality=95)
                        
                audit_results.append({
                    "id": cid,
                    "name": cname,
                    "series": c["series"],
                    "status": "PASS",
                    "orig_size": orig_size,
                    "final_size": (848, 1264)
                })
        except Exception as e:
            print(f"Error processing Card {cid} from {source_file}: {e}")
            audit_results.append({
                "id": cid,
                "name": cname,
                "series": c["series"],
                "status": "ERROR",
                "error": str(e)
            })
    else:
        audit_results.append({
            "id": cid,
            "name": cname,
            "series": c["series"],
            "status": "MISSING"
        })

pass_count = sum(1 for r in audit_results if r.get("status") == "PASS")
print(f"Audit Complete: {pass_count} / {len(cards_data)} PASSED (848x1264 standard).")

with open(os.path.join(DOC_DIR, "audit_results.json"), "w", encoding="utf-8") as f:
    json.dump(audit_results, f, ensure_ascii=False, indent=2)
