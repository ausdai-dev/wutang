with open("frontend/_template.html", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if 'wutang-data' in line:
            print(f"{idx}: {line.strip()[:100]}")
