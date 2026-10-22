with open("frontend/_template.html", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if idx > 7100 and any(k in line for k in ['<nav', 'class="nav', 'mode-btn', 'header-nav', 'data-mode']):
            print(f"{idx}: {line.strip()[:100]}")
