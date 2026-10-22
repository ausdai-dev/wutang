import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("frontend/_template.html", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if 'tabCards' in line:
            print(f"{idx}: {line.strip()[:100]}")
