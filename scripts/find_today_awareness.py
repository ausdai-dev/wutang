# -*- coding: utf-8 -*-
with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'今日觉察', text)]
for idx in matches:
    start = max(0, idx - 100)
    end = min(len(text), idx + 400)
    print("--- MATCH ---")
    print(text[start:end])
