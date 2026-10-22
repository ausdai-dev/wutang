# -*- coding: utf-8 -*-
with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'<button class="nav-btn[^"]*"[^>]*>[\s\S]*?</button>', text)
print("Nav buttons:")
for b in matches:
    print(" ", b.strip().replace('\n', ' '))
