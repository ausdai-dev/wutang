import re

with open("frontend/_template.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Total lines:", len(lines))

for idx, line in enumerate(lines, 1):
    if any(k in line for k in ['id="viewUserResult"', 'id="userResult"', 'id="clientResult"']):
        print(f"View line: {idx}: {line.strip()[:100]}")
    if any(k in line for k in ['resCardMindset', 'resCardWisdom', 'resCardAction']):
        print(f"Card element line: {idx}: {line.strip()[:100]}")
