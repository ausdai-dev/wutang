with open("frontend/_template.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(10965, 11010):
    print(f"{i+1}: {lines[i]}", end="")
