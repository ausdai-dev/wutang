# -*- coding: utf-8 -*-
"""
悟堂解忧团 —— 占位头像生成
512x512 PNG，统一「宣纸底 + 印章色块 + 单字」风格。
用托管 venv 的 Pillow 绘制；如需 AI 生成的头像，可用 ImageGen 逐张替换
（见 references/avatar-spec.md，注意按张计费）。
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = r"C:/Users/ausda/.workbuddy-ai/plugins/marketplaces/my-experts/plugins/wutang-relief/avatars"
PAPER = (251, 247, 240)
INK = (43, 39, 36)
LINE = (228, 220, 207)

ROLES = [
    ("team",                    "悟", (140, 58, 43),  True),
    ("wutang-relief-team-lead", "川", (140, 58, 43),  False),
    ("empathy-listener",        "听", (168, 97, 62),  False),
    ("classics-officer",        "据", (74, 107, 79),  False),
    ("micro-action-coach",      "步", (63, 90, 122),  False),
    ("safety-gatekeeper",       "守", (74, 85, 104),  False),
    ("content-chief-editor",    "锦", (176, 138, 74), False),
]

FONT_CANDIDATES = [
    r"C:/Windows/Fonts/msyhbd.ttc",
    r"C:/Windows/Fonts/simhei.ttf",
    r"C:/Windows/Fonts/msyh.ttc",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def make(name, ch, color, is_team):
    S = 512
    img = Image.new("RGB", (S, S), PAPER)
    d = ImageDraw.Draw(img)

    # 外框
    d.rounded_rectangle([16, 16, S - 16, S - 16], radius=18, outline=LINE, width=2)
    # 内框
    d.rounded_rectangle([30, 30, S - 30, S - 30], radius=12, outline=LINE, width=1)

    # 色块
    if is_team:
        d.rounded_rectangle([104, 104, S - 104, S - 104], radius=20, fill=color)
        d.rounded_rectangle([120, 120, S - 120, S - 120], radius=12, outline=PAPER, width=3)
    else:
        d.ellipse([120, 120, S - 120, S - 120], fill=color)
        d.ellipse([136, 136, S - 136, S - 136], outline=PAPER, width=3)

    # 主字
    f = load_font(210 if is_team else 230)
    bb = d.textbbox((0, 0), ch, font=f)
    d.text(((S - (bb[2] - bb[0])) / 2 - bb[0], (S - (bb[3] - bb[1])) / 2 - bb[1] - 8),
           ch, font=f, fill=PAPER)

    # 底部细线 + 品牌小字
    d.line([S / 2 - 46, S - 74, S / 2 + 46, S - 74], fill=LINE, width=2)
    f2 = load_font(20)
    label = "悟堂解忧团" if is_team else "悟堂"
    bb2 = d.textbbox((0, 0), label, font=f2)
    d.text(((S - (bb2[2] - bb2[0])) / 2 - bb2[0], S - 62), label, font=f2, fill=(122, 115, 108))

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{name}.png")
    img.save(path, "PNG", optimize=True)
    return path, os.path.getsize(path)


if __name__ == "__main__":
    total = 0
    for name, ch, color, is_team in ROLES:
        p, sz = make(name, ch, color, is_team)
        total += sz
        print(f"  {os.path.basename(p):34s} {sz/1024:6.1f} KB  「{ch}」")
    print(f"[ok] {len(ROLES)} 张头像，合计 {total/1024:.1f} KB（单张均 < 500KB，512x512）")
