with open("frontend/_template.html", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if 'id="cardsArea"' in line or 'id="viewCards"' in line or 'cardsArea' in line:
            print(f"{idx}: {line.strip()[:100]}")
