with open("frontend/_template.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(7135, 7185):
    print(f"{i+1}: {lines[i].strip()}")
