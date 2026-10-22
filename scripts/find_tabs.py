# -*- coding: utf-8 -*-
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.findall(r'<button[^>]*class="[^"]*mode-tab[^"]*"[^>]*>', content)
print(f"Found {len(matches)} mode-tab buttons:")
for m in matches:
    print(" ", m)
