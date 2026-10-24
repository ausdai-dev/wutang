# -*- coding: utf-8 -*-
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_path = os.path.join(ROOT, "frontend", "index.html")

with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

checks = [
    ("Audio element <audio id='bgmAudio'> present", 'id="bgmAudio"' in content),
    ("BGM toggle button <button id='btnBgmToggle'> in header", 'id="btnBgmToggle"' in content),
    ("BGM dropdown panel <div id='bgmPanel'> present", 'id="bgmPanel"' in content),
    ("BGM track list container <div id='bgmTrackList'> present", 'id="bgmTrackList"' in content),
    ("BGM floating pill <div id='bgmFloatingPill'> removed (clean UI)", 'id="bgmFloatingPill"' not in content),
    ("Flowing Mind track referenced", "flowing_mind.m4a" in content),
    ("Zen Meditation track referenced", "zen_meditation.m4a" in content),
    ("bgmEngine initialized in bootstrap()", "bgmEngine.init()" in content),
    ("Flowing Mind audio file exists in assets/audio", os.path.exists(os.path.join(ROOT, "frontend", "assets", "audio", "Flowing Mind.m4a"))),
    ("Zen Meditation audio file exists in assets/audio", os.path.exists(os.path.join(ROOT, "frontend", "assets", "audio", "Zen Meditation.m4a"))),
    ("Web-safe flowing_mind.m4a alias exists", os.path.exists(os.path.join(ROOT, "frontend", "assets", "audio", "flowing_mind.m4a"))),
    ("Web-safe zen_meditation.m4a alias exists", os.path.exists(os.path.join(ROOT, "frontend", "assets", "audio", "zen_meditation.m4a"))),
]

all_pass = True
print("==================================================")
print("🎵 悟堂 · 禅意背景音乐全量组件验收")
print("==================================================")
for name, ok in checks:
    status = "✓" if ok else "✗"
    print(f"  [{status}] {name}")
    if not ok:
        all_pass = False

print("==================================================")
print(f"验收结果: {'全部通过 (PASS)' if all_pass else '存在未通过项 (FAIL)'}")
print("==================================================")
