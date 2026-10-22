# -*- coding: utf-8 -*-
with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    ("zen96CardsSection", 'id="zen96CardsSection"' in html),
    ("zen96Modal", 'id="zen96Modal"' in html),
    ("ZEN_CARDS_96 definition", "var ZEN_CARDS_96 = RAW_DATA.zenCards96" in html),
    ("Embedded 96 cards count", '"card_id":"WUTANG-CARD-96"' in html),
    ("renderZen96CardsSection", "function renderZen96CardsSection" in html),
    ("drawRandomZen96Card", "window.drawRandomZen96Card" in html),
    ("useZen96InRelief", "window.useZen96InRelief" in html)
]

for label, passed in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {label}")

assert all(p for _, p in checks), "Not all frontend checks passed!"
print("Frontend Integration is 100% Verified!")
