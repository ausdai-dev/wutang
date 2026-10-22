# -*- coding: utf-8 -*-
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'THEME_PACKS', text)]
for idx in matches:
    start = max(0, idx - 50)
    end = min(len(text), idx + 800)
    print("--- THEME_PACKS MATCH ---")
    print(text[start:end])
