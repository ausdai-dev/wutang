# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 禅、茶、竹 意境 UI 底图与视觉装饰生成引擎
批量生成：
1. 全局温润宣纸茶晕底纹 (zen_paper_bg.png)
2. 窗纱竹影角花暗纹 (bamboo_corner.png)
3. 烹茶静心水印 (tea_bowl_vignette.png)
4. 枯山水涟漪禅石底纹 (zen_ripple_corner.png)
5. 3 款全新东方解忧书笺：
   - 云林茶隐笺 (bm_tea_sanctuary.png)
   - 修竹清风笺 (bm_bamboo_shadow.png)
   - 枯山静水笺 (bm_zen_stone.png)
"""

import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI_DIR = os.path.join(ROOT, "frontend", "assets", "ui")
BOOKMARK_DIR = os.path.join(ROOT, "frontend", "assets", "bookmarks")
os.makedirs(UI_DIR, exist_ok=True)
os.makedirs(BOOKMARK_DIR, exist_ok=True)

def get_font(size=24):
    for p in [r"C:/Windows/Fonts/simkai.ttf", r"C:/Windows/Fonts/simsun.ttc", r"C:/Windows/Fonts/msyh.ttc"]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

# 1. 生成全局温润宣纸与茶晕底纹 (平铺式无缝纹理)
def make_paper_tea_bg(w=500, h=500):
    img = Image.new("RGBA", (w, h), (249, 246, 240, 255))
    draw = ImageDraw.Draw(img)
    
    # 细密植物纤维杂质
    random.seed(108)
    for _ in range(w * h // 120):
        fx = random.randint(0, w - 1)
        fy = random.randint(0, h - 1)
        length = random.randint(2, 5)
        angle = random.uniform(0, math.pi * 2)
        dx = int(math.cos(angle) * length)
        dy = int(math.sin(angle) * length)
        draw.line([(fx, fy), (fx + dx, fy + dy)], fill=(160, 148, 130, random.randint(8, 18)), width=1)
        
    # 茶晕淡渍 (极柔和渐变，透明度极低，增加自然温润感)
    tea_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(tea_overlay)
    for _ in range(5):
        cx = random.randint(50, w - 50)
        cy = random.randint(50, h - 50)
        r = random.randint(80, 160)
        tdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(198, 172, 130, random.randint(5, 12)))
    tea_overlay = tea_overlay.filter(ImageFilter.GaussianBlur(40))
    
    img = Image.alpha_composite(img, tea_overlay)
    path = os.path.join(UI_DIR, "zen_paper_bg.png")
    img.save(path, "PNG", optimize=True)
    print(f"[OK] 生成全局宣纸茶晕底纹: {path}")

# 2. 生成窗纱竹影角花暗纹 (透明 PNG，用于页面右上角/卡片角隅)
def make_bamboo_corner(w=380, h=380):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 从右上角斜入的优雅墨竹
    color = (54, 76, 62) # 雅致竹青
    
    def draw_leaf(lx, ly, angle_deg, length=45, width=10, alpha=160):
        rad = math.radians(angle_deg)
        pts = []
        steps = 10
        for i in range(steps + 1):
            t = i / steps
            dist = length * t
            w_cur = width * math.sin(t * math.pi)
            px = lx + math.cos(rad) * dist - math.sin(rad) * (w_cur / 2)
            py = ly + math.sin(rad) * dist + math.cos(rad) * (w_cur / 2)
            pts.append((px, py))
        for i in range(steps, -1, -1):
            t = i / steps
            dist = length * t
            w_cur = width * math.sin(t * math.pi)
            px = lx + math.cos(rad) * dist + math.sin(rad) * (w_cur / 2)
            py = ly + math.sin(rad) * dist - math.cos(rad) * (w_cur / 2)
            pts.append((px, py))
        draw.polygon(pts, fill=(*color, alpha))
        
    # 主竹竿 1
    start_x, start_y = w + 20, -20
    end_x, end_y = w - 160, h
    draw.line([(start_x, start_y), (end_x, end_y)], fill=(*color, 140), width=4)
    # 竹节
    for t in [0.25, 0.55, 0.82]:
        nx = start_x + (end_x - start_x) * t
        ny = start_y + (end_y - start_y) * t
        draw.line([(nx - 8, ny - 3), (nx + 8, ny + 3)], fill=(*color, 180), width=5)
        # 从节间生出小枝
        bx = nx - 4
        by = ny
        b_end_x = bx - 60
        b_end_y = by + 35
        draw.line([(bx, by), (b_end_x, b_end_y)], fill=(*color, 150), width=2)
        # 竹叶簇
        draw_leaf(b_end_x, b_end_y, 140, length=55, width=12, alpha=150)
        draw_leaf(b_end_x, b_end_y, 165, length=45, width=10, alpha=130)
        draw_leaf(b_end_x, b_end_y, 120, length=40, width=9, alpha=120)

    # 次竹竿 2
    s2_x, s2_y = w - 50, -30
    e2_x, e2_y = w - 240, h - 60
    draw.line([(s2_x, s2_y), (e2_x, e2_y)], fill=(*color, 80), width=3)
    for t in [0.35, 0.7]:
        nx = s2_x + (e2_x - s2_x) * t
        ny = s2_y + (e2_y - s2_y) * t
        draw.line([(nx - 6, ny - 2), (nx + 6, ny + 2)], fill=(*color, 110), width=4)
        draw_leaf(nx - 40, ny + 20, 155, length=48, width=11, alpha=90)
        draw_leaf(nx - 35, ny + 25, 180, length=38, width=8, alpha=80)
        
    # 轻微高斯模糊制造窗纱后的透光剪影质感
    img = img.filter(ImageFilter.GaussianBlur(1))
    path = os.path.join(UI_DIR, "bamboo_corner.png")
    img.save(path, "PNG", optimize=True)
    print(f"[OK] 生成窗纱竹影角花: {path}")

# 3. 生成烹茶静心水印 (tea_bowl_vignette.png)
def make_tea_vignette(w=360, h=300):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = w // 2, h - 80
    ink = (85, 75, 65)
    
    # 茶席木托 / 阴影
    draw.ellipse([cx - 90, cy + 32, cx + 90, cy + 46], fill=(180, 165, 150, 45))
    
    # 宋代盏托与茶盏
    # 盏身曲线 (圆弧多边形)
    pts = [
        (cx - 70, cy),
        (cx - 50, cy + 34),
        (cx + 50, cy + 34),
        (cx + 70, cy)
    ]
    # 盏身淡青釉色
    draw.polygon(pts, fill=(135, 160, 152, 90), outline=(*ink, 140))
    # 盏口椭圆
    draw.ellipse([cx - 70, cy - 14, cx + 70, cy + 14], fill=(160, 182, 175, 110), outline=(*ink, 160), width=2)
    # 茶汤清澈内圈
    draw.ellipse([cx - 60, cy - 10, cx + 60, cy + 10], fill=(188, 172, 120, 150))
    
    # 袅袅升起的温润茶烟 (贝塞尔波浪曲线模拟)
    steam_color = (165, 155, 145)
    for idx, sx_offset in enumerate([-20, 4, 25]):
        steam_pts = []
        base_sx = cx + sx_offset
        for step in range(60):
            t = step / 60
            sy = cy - 20 - t * 140
            drift = math.sin(t * math.pi * 3 + idx) * (14 + t * 24)
            steam_pts.append((base_sx + drift, sy))
            
        for si in range(len(steam_pts) - 1):
            t = si / len(steam_pts)
            alpha = int(140 * math.sin(t * math.pi))
            draw.line([steam_pts[si], steam_pts[si + 1]], fill=(*steam_color, alpha), width=int(3 - t * 2))
            
    img = img.filter(ImageFilter.GaussianBlur(1))
    path = os.path.join(UI_DIR, "tea_bowl_vignette.png")
    img.save(path, "PNG", optimize=True)
    print(f"[OK] 生成烹茶静心水印: {path}")

# 4. 生成枯山水涟漪与禅石底纹 (zen_ripple_corner.png)
def make_zen_ripple_corner(w=360, h=360):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = 90, h - 90
    color = (120, 110, 100)
    
    # 枯山水同心微波
    for r in range(16, 260, 18):
        alpha = max(10, int(75 * (1.0 - r / 260)))
        draw.ellipse([cx - r, cy - r * 0.5, cx + r, cy + r * 0.5], outline=(*color, alpha), width=1)
        
    # 禅石 (圆润光滑卵石)
    stone_pts = [
        (cx - 32, cy - 4),
        (cx - 18, cy - 22),
        (cx + 14, cy - 20),
        (cx + 34, cy - 2),
        (cx + 24, cy + 16),
        (cx - 10, cy + 20),
        (cx - 28, cy + 10)
    ]
    draw.polygon(stone_pts, fill=(95, 90, 85, 160))
    # 禅石高光
    draw.ellipse([cx - 12, cy - 14, cx + 8, cy - 6], fill=(160, 155, 148, 120))
    
    img = img.filter(ImageFilter.GaussianBlur(1))
    path = os.path.join(UI_DIR, "zen_ripple_corner.png")
    img.save(path, "PNG", optimize=True)
    print(f"[OK] 生成枯山水禅石底纹: {path}")

# 5. 生成 3 款全新禅、茶、竹专属书笺
def make_new_zen_bookmarks():
    # A. 云林茶隐笺
    bw, bh = 420, 900
    img_tea = Image.new("RGBA", (bw, bh), (252, 248, 240, 255))
    d_tea = ImageDraw.Draw(img_tea)
    
    # 细碎茶末纤维
    random.seed(99)
    for _ in range(bw * bh // 160):
        rx, ry = random.randint(0, bw - 1), random.randint(0, bh - 1)
        d_tea.point((rx, ry), fill=(180, 150, 105, random.randint(20, 60)))
        
    # 茶盏与茶烟
    tea_wig = Image.open(os.path.join(UI_DIR, "tea_bowl_vignette.png"))
    img_tea.paste(tea_wig, (bw - 300, bh - 320), tea_wig)
    
    # 双层茶褐色边框
    border_tea = (195, 165, 125)
    d_tea.rounded_rectangle([20, 68, bw - 20, bh - 24], radius=6, outline=border_tea, width=2)
    d_tea.rounded_rectangle([26, 74, bw - 26, bh - 30], radius=4, outline=(*border_tea, 120), width=1)
    # 顶孔
    d_tea.ellipse([bw // 2 - 10, 28, bw // 2 + 10, 48], outline=(186, 148, 86), width=2)
    d_tea.ellipse([bw // 2 - 6, 32, bw // 2 + 6, 44], fill=(230, 222, 210))
    d_tea.line([(bw // 2, 48), (bw // 2, 64)], fill=(148, 44, 38), width=2)
    
    # 题头
    font = get_font(13)
    d_tea.text((bw // 2 - 58, 100), "悟 堂 · 云 林 茶 隐 笺", font=font, fill=(138, 92, 62))
    d_tea.text((bw // 2 - 110, bh - 55), "一 盏 清 茗 酬 知 己 · 半 日 闲 暇 读 诗 书", font=font, fill=(135, 128, 120))
    tea_path = os.path.join(BOOKMARK_DIR, "bm_tea_sanctuary.png")
    img_tea.save(tea_path, "PNG", optimize=True)
    print(f"[OK] 生成云林茶隐笺: {tea_path}")

    # B. 修竹清风笺
    img_bamboo = Image.new("RGBA", (bw, bh), (247, 250, 247, 255))
    d_bm = ImageDraw.Draw(img_bamboo)
    bamboo_wig = Image.open(os.path.join(UI_DIR, "bamboo_corner.png"))
    img_bamboo.paste(bamboo_wig, (bw - 360, 80), bamboo_wig)
    
    border_bam = (185, 210, 192)
    d_bm.rounded_rectangle([20, 68, bw - 20, bh - 24], radius=6, outline=border_bam, width=2)
    d_bm.rounded_rectangle([26, 74, bw - 26, bh - 30], radius=4, outline=(*border_bam, 130), width=1)
    d_bm.ellipse([bw // 2 - 10, 28, bw // 2 + 10, 48], outline=(186, 148, 86), width=2)
    d_bm.ellipse([bw // 2 - 6, 32, bw // 2 + 6, 44], fill=(230, 222, 210))
    d_bm.line([(bw // 2, 48), (bw // 2, 64)], fill=(148, 44, 38), width=2)
    d_bm.text((bw // 2 - 58, 100), "悟 堂 · 修 竹 清 风 笺", font=font, fill=(54, 88, 73))
    d_bm.text((bw // 2 - 110, bh - 55), "虚 心 劲 节 凌 云 气 · 疏 影 摇 风 自 得 闲", font=font, fill=(110, 130, 115))
    bam_path = os.path.join(BOOKMARK_DIR, "bm_bamboo_shadow.png")
    img_bamboo.save(bam_path, "PNG", optimize=True)
    print(f"[OK] 生成修竹清风笺: {bam_path}")

    # C. 枯山静水笺
    img_zen = Image.new("RGBA", (bw, bh), (250, 248, 245, 255))
    d_zen = ImageDraw.Draw(img_zen)
    zen_wig = Image.open(os.path.join(UI_DIR, "zen_ripple_corner.png"))
    img_zen.paste(zen_wig, (20, bh - 360), zen_wig)
    
    border_zen = (205, 195, 182)
    d_zen.rounded_rectangle([20, 68, bw - 20, bh - 24], radius=6, outline=border_zen, width=2)
    d_zen.rounded_rectangle([26, 74, bw - 26, bh - 30], radius=4, outline=(*border_zen, 120), width=1)
    d_zen.ellipse([bw // 2 - 10, 28, bw // 2 + 10, 48], outline=(186, 148, 86), width=2)
    d_zen.ellipse([bw // 2 - 6, 32, bw // 2 + 6, 44], fill=(230, 222, 210))
    d_zen.line([(bw // 2, 48), (bw // 2, 64)], fill=(148, 44, 38), width=2)
    d_zen.text((bw // 2 - 58, 100), "悟 堂 · 枯 山 静 水 笺", font=font, fill=(90, 85, 80))
    d_zen.text((bw // 2 - 110, bh - 55), "风 定 水 澄 涵 万 象 · 磐 石 不 语 自 禅 心", font=font, fill=(130, 125, 118))
    zen_path = os.path.join(BOOKMARK_DIR, "bm_zen_stone.png")
    img_zen.save(zen_path, "PNG", optimize=True)
    print(f"[OK] 生成枯山静水笺: {zen_path}")

def main():
    print("=== 开始生成悟堂 禅、茶、竹 视觉意境底图与书笺 ===")
    make_paper_tea_bg()
    make_bamboo_corner()
    make_tea_vignette()
    make_zen_ripple_corner()
    make_new_zen_bookmarks()
    print("=== UI 意境底图与新书笺生成完毕 ===")

if __name__ == "__main__":
    main()
