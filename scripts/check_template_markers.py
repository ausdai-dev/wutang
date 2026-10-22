import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("frontend/_template.html", "r", encoding="utf-8") as f:
    content = f.read()

print("File size:", len(content))
print("Has userTextarea:", "id=\"userTextarea\"" in content)
print("Has resCardWisdom:", "id=\"resCardWisdom\"" in content)
print("Has tabCards:", "id=\"tabCards\"" in content)
print("Has updateStreamingFourStep:", "function updateStreamingFourStep" in content)
