with open("frontend/_template.html", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if any(k in line for k in ['galleryGrid', 'viewGallery', 'themePacksGrid', 'pantheon', 'mode-cards']):
            print(f"{idx}: {line.strip()[:100]}")
