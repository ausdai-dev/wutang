with open("frontend/_template.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract script blocks
import re
scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL)
print("Found script blocks:", len(scripts))

for idx, s in enumerate(scripts):
    with open(f"scripts/temp_script_{idx}.js", "w", encoding="utf-8") as out:
        out.write(s)
    print(f"Wrote temp_script_{idx}.js, size: {len(s)}")
