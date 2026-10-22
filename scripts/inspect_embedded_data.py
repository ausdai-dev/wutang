# -*- coding: utf-8 -*-
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re, json
m = re.search(r'<script id="wutang-data" type="application/json">([\s\S]*?)</script>', text)
if m:
    data = json.loads(m.group(1))
    print("Embedded wutang-data keys:", list(data.keys()))
    if 'themePacks' in data:
        print("themePacks:", [(p['pack_id'], p['name']) for p in data['themePacks']])
