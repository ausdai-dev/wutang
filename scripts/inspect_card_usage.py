# -*- coding: utf-8 -*-
import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'assets/cards/[^\s\"\'\<\>]+', text)
print('Unique card asset references in index.html:', set(matches))

# Look for card draw or divination or wisdom card logic
keywords = ['抽卡', '抽签', '今日觉察', '卡牌', 'cards', 'zen_cards', 'manifest']
for kw in keywords:
    count = text.count(kw)
    print(f'Occurrences of "{kw}": {count}')
