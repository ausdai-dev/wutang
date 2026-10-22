# -*- coding: utf-8 -*-
with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('id="entryCardArea"')
if idx != -1:
    print(text[idx-50:idx+1500])
