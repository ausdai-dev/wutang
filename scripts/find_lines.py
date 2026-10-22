# -*- coding: utf-8 -*-
with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '<main id="cardsArea"' in l:
        print(f"cardsArea line: {i+1}")
    if 'function renderCardsSection' in l:
        print(f"renderCardsSection line: {i+1}")
    if 'var THEME_PACKS' in l:
        print(f"var THEME_PACKS line: {i+1}")
