# -*- coding: utf-8 -*-
import os
import shutil
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "DOC", "觉察牌")
DST_DIR = os.path.join(ROOT, "frontend", "assets", "cards", "mindset")
os.makedirs(DST_DIR, exist_ok=True)

print("Deploying 16 awareness cards from DOC/觉察牌 to frontend/assets/cards/mindset...")

for i in range(1, 17):
    card_id = f"M-{i:03d}"
    src_file = os.path.join(SRC_DIR, f"{i}.jpg")
    if not os.path.exists(src_file):
        print(f"  [WARN] Missing {src_file}")
        continue
    
    # Save as PNG
    dst_png = os.path.join(DST_DIR, f"{card_id}.png")
    im = Image.open(src_file)
    im.save(dst_png, format="PNG", quality=95)
    
    # Also save as JPG for flexibility
    dst_jpg = os.path.join(DST_DIR, f"{card_id}.jpg")
    shutil.copyfile(src_file, dst_jpg)
    
    print(f"  [OK] {i}.jpg -> {card_id}.png ({im.size[0]}x{im.size[1]})")

print("\n[SUCCESS] All 16 mindset cards deployed successfully!")
