# -*- coding: utf-8 -*-
with open("frontend/_template.html", "r", encoding="utf-8") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'historyCardListContainer', text)]
for m in matches:
    line_no = text[:m].count('\n') + 1
    print(f"Line {line_no}: {text[max(0, m-80):min(len(text), m+120)].strip()}")
