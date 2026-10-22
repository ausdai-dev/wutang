# -*- coding: utf-8 -*-
with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'function renderAwarenessCard' in l:
        print(f"renderAwarenessCard at line {i+1}")
        for j in range(i, min(len(lines), i+40)):
            print(f"  {j+1}: {lines[j].rstrip()}")
        break
