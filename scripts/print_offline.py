import sys
sys.stdout.reconfigure(encoding='utf-8')
with open("frontend/_template.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in range(15110, 15130):
    print(f"{i+1}: {lines[i]}", end="")
