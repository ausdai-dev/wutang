# -*- coding: utf-8 -*-
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'card_universal_front' in line or 'card-flip' in line or 'zen-card' in line or 'id="card' in line:
        print(f"Line {i+1}: {line.strip()[:100]}")
