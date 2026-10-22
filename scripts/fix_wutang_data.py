with open("frontend/_template.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace invalid occurrences of __WUTANG_DATA__ in JS
content = content.replace("window.__WUTANG_DATA__ && window.__WUTANG_DATA__.zenCards108", "typeof ZEN_CARDS_108 !== 'undefined' && ZEN_CARDS_108")
content = content.replace("window.__WUTANG_DATA__.zenCards108", "ZEN_CARDS_108")

# 2. Add ZEN_CARDS_108 definition after RAW_DATA
TARGET_RAW = "var ZEN_ASSETS = RAW_DATA.zenAssets || { cards: {}, bookmarks: {} };"
REPLACEMENT_RAW = "var ZEN_ASSETS = RAW_DATA.zenAssets || { cards: {}, bookmarks: {} };\n  var ZEN_CARDS_108 = RAW_DATA.zenCards108 || [];"

if TARGET_RAW in content and "var ZEN_CARDS_108" not in content:
    content = content.replace(TARGET_RAW, REPLACEMENT_RAW, 1)
    print("[ok] Added ZEN_CARDS_108 declaration")

with open("frontend/_template.html", "w", encoding="utf-8") as f:
    f.write(content)

print("[ok] Cleaned up frontend/_template.html")
