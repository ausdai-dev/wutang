# -*- coding: utf-8 -*-
import os
import re

with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

areas = ['clientArea', 'growthArea', 'wellbeingArea', 'practiceArea', 'cardsArea', 'mineArea', 'studioArea']
for a in areas:
    exists = f'id="{a}"' in content
    print(f"Area {a}: {'EXISTS' if exists else 'MISSING'}")
