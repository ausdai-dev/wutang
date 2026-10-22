# -*- coding: utf-8 -*-
import json

with open(r'd:\BaiduSyncdisk\02-DEV\悟堂\DOC\cards_parsed.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

for i, c in enumerate(cards):
    print(f"{c['id']}: [{c['series']}] {c['name']}", end=" | " if (i+1)%4 != 0 else "\n")
