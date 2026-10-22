with open("frontend/_template.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(15112, 15132):
    print(repr(lines[i]))
