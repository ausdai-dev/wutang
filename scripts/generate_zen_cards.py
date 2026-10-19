# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 东方禅意卡牌与书笺批量生成引擎 (PRD 2.0 工业版)
结合 PRD 2.0 规范与 500 条经典数据库的 6 大分类 + 4 大场景 + 3 大卡牌类型，
批量生成高雅、轻量、东方极简美学的卡牌（正反面）与书笺（东方解忧笺）图案。
"""

import os
import math
import random
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD_DIR = os.path.join(ROOT, "frontend", "assets", "cards")
BOOKMARK_DIR = os.path.join(ROOT, "frontend", "assets", "bookmarks")
os.makedirs(os.path.join(CARD_DIR, "front"), exist_ok=True)
os.makedirs(os.path.join(CARD_DIR, "back"), exist_ok=True)
os.makedirs(BOOKMARK_DIR, exist_ok=True)

# 基础像素尺寸 (轻量、Retina 清晰、快速加载)
CARD_W, CARD_H = 480, 720        # 卡牌 2:3 黄金比例
BOOKMARK_W, BOOKMARK_H = 420, 900 # 书笺 7:15 雅致长条比例

# 字体加载
def get_font(font_name="simkai", size=24):
    font_map = {
        "simkai": r"C:/Windows/Fonts/simkai.ttf",
        "simsun": r"C:/Windows/Fonts/simsun.ttc",
        "msyh": r"C:/Windows/Fonts/msyh.ttc",
        "simfang": r"C:/Windows/Fonts/simfang.ttf",
    }
    path = font_map.get(font_name, r"C:/Windows/Fonts/simkai.ttf")
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

# 传统东方矿物色彩库
PALETTE = {
    "paper_base": (251, 247, 240),       # 宣纸白
    "paper_warm": (249, 244, 233),       # 暖熟宣
    "paper_cool": (245, 247, 247),       # 玉版宣
    "ink_pure": (34, 30, 27),            # 浓墨
    "ink_medium": (70, 65, 60),          # 焦墨 / 炭黑
    "ink_light": (135, 128, 120),        # 淡墨
    "ink_wash": (210, 204, 195),         # 极淡墨韵
    "vermilion": (148, 44, 38),          # 经典朱砂红
    "vermilion_deep": (126, 32, 28),     # 熟赭暗红
    "gold_antique": (186, 148, 86),      # 泥金
    "gold_light": (214, 185, 133),       # 浅泥金
    "pine_green": (54, 88, 73),          # 松柏青绿
    "bamboo_green": (78, 116, 92),       # 竹青
    "celadon": (112, 142, 134),          # 影青瓷
    "indigo_blue": (48, 72, 92),         # 霁蓝黛青
    "ochre_brown": (138, 92, 62),        # 赭石
    "stone_gray": (88, 96, 105),         # 苍石青灰
    "border_sand": (224, 214, 198),      # 雅致泥线
    "border_gold": (202, 172, 120),      # 泥金细线
}

def create_xuan_paper(w, h, base_color=(251, 247, 240), texture_level=12):
    """生成带有细腻温润纤维感的宣纸纹理底图"""
    img = Image.new("RGBA", (w, h), (*base_color, 255))
    draw = ImageDraw.Draw(img)
    
    # 细密微小纸浆纤维杂质 (东方古法手工宣纸质感)
    random.seed(42)
    for _ in range(w * h // 180):
        fx = random.randint(0, w - 1)
        fy = random.randint(0, h - 1)
        length = random.randint(2, 6)
        angle = random.uniform(0, math.pi * 2)
        dx = int(math.cos(angle) * length)
        dy = int(math.sin(angle) * length)
        fiber_alpha = random.randint(6, 16)
        draw.line([(fx, fy), (fx + dx, fy + dy)], fill=(150, 140, 125, fiber_alpha), width=1)
        
    return img

def draw_classical_corners(draw, x1, y1, x2, y2, color, size=18):
    """绘制传统古典回纹 / 如意纹角花"""
    # 左上
    draw.line([(x1, y1 + size), (x1, y1), (x1 + size, y1)], fill=color, width=2)
    draw.line([(x1 + 4, y1 + size - 4), (x1 + 4, y1 + 4), (x1 + size - 4, y1 + 4)], fill=color, width=1)
    draw.point([(x1 + 8, y1 + 8)], fill=color)
    
    # 右上
    draw.line([(x2 - size, y1), (x2, y1), (x2, y1 + size)], fill=color, width=2)
    draw.line([(x2 - size + 4, y1 + 4), (x2 - 4, y1 + 4), (x2 - 4, y1 + size - 4)], fill=color, width=1)
    draw.point([(x2 - 8, y1 + 8)], fill=color)
    
    # 左下
    draw.line([(x1, y2 - size), (x1, y2), (x1 + size, y2)], fill=color, width=2)
    draw.line([(x1 + 4, y2 - size + 4), (x1 + 4, y2 - 4), (x1 + size - 4, y2 - 4)], fill=color, width=1)
    draw.point([(x1 + 8, y2 - 8)], fill=color)
    
    # 右下
    draw.line([(x2 - size, y2), (x2, y2), (x2, y2 - size)], fill=color, width=2)
    draw.line([(x2 - size + 4, y2 - 4), (x2 - 4, y2 - 4), (x2 - 4, y2 - size + 4)], fill=color, width=1)
    draw.point([(x2 - 8, y2 - 8)], fill=color)

def draw_zen_seal(draw, cx, cy, size, text, bg_color=PALETTE["vermilion"], font_color=(254, 252, 248)):
    """绘制高古朱砂篆印"""
    half = size // 2
    # 印章底色 (略带手工刀痕的圆角方印)
    draw.rounded_rectangle([cx - half, cy - half, cx + half, cy + half], radius=4, fill=bg_color)
    # 印泥微渗边线
    draw.rounded_rectangle([cx - half + 2, cy - half + 2, cx + half - 2, cy + half - 2], radius=3, outline=(230, 200, 190, 140), width=1)
    
    # 印文字体
    f_size = int(size * 0.65)
    font = get_font("simkai", f_size)
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2 - 2), text, font=font, fill=font_color)

def draw_enso(draw, cx, cy, radius, ink_color=PALETTE["ink_pure"]):
    """绘制一笔水墨禅圈 (円相 Enso) —— 象征觉悟、圆满与虚空留白"""
    steps = 140
    start_angle = -math.pi * 0.75
    end_angle = math.pi * 1.15
    arc_len = end_angle - start_angle
    
    for i in range(steps):
        t = i / steps
        angle = start_angle + arc_len * t
        
        # 笔势粗细起伏变化：起笔轻，中段饱满，尾段飞白出锋
        if t < 0.15:
            thickness = 4 + 18 * (t / 0.15)
            alpha = int(120 + 130 * (t / 0.15))
        elif t < 0.75:
            thickness = 22 + 8 * math.sin((t - 0.15) / 0.6 * math.pi)
            alpha = 240
        else:
            fade = (1.0 - t) / 0.25
            thickness = 3 + 22 * fade
            alpha = int(60 + 180 * fade)
            
        r = radius + math.sin(t * 8) * 3
        px = cx + math.cos(angle) * r
        py = cy + math.sin(angle) * r
        
        # 绘制笔触圆形
        col = (*ink_color[:3], int(alpha * 0.85))
        draw.ellipse([px - thickness/2, py - thickness/2, px + thickness/2, py + thickness/2], fill=col)

def draw_misty_mountains(draw, w, h, base_y, ink_color):
    """绘制意境深远的水墨叠峦远岫"""
    for layer in range(3):
        pts = [(0, h)]
        step_x = 16
        y_offset = base_y + layer * 28
        freq = 0.008 + layer * 0.004
        alpha = int(25 + layer * 30)
        
        for x in range(0, w + step_x, step_x):
            y = y_offset - 25 * math.sin(x * freq + layer) - 15 * math.cos(x * freq * 1.8)
            pts.append((x, y))
            
        pts.append((w, h))
        draw.polygon(pts, fill=(*ink_color[:3], alpha))

def draw_bamboo_branch(draw, x, y, height, color):
    """绘制淡雅竹枝与竹叶"""
    num_nodes = 4
    seg_h = height / num_nodes
    curr_y = y + height
    
    for i in range(num_nodes):
        next_y = curr_y - seg_h + 3
        draw.line([(x, curr_y), (x, next_y)], fill=color, width=2)
        # 竹节
        draw.line([(x - 4, next_y), (x + 4, next_y)], fill=color, width=3)
        
        # 竹叶
        if i % 2 == 1:
            leaf_dir = 1 if (i // 2) % 2 == 0 else -1
            draw.line([(x, next_y), (x + leaf_dir * 24, next_y - 12)], fill=color, width=2)
            draw.line([(x, next_y), (x + leaf_dir * 18, next_y - 6)], fill=color, width=2)
            
        curr_y = next_y

def draw_concentric_zen_ripples(draw, cx, cy, max_r, color):
    """绘制枯山水水纹 / 同心静水涟漪"""
    for r in range(18, max_r, 16):
        alpha = max(10, int(60 * (1.0 - r / max_r)))
        draw.ellipse([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], outline=(*color[:3], alpha), width=1)


# =========================================================================
# 核心生成器 1：卡牌正面背景边框模板 (Front Card Frame)
# =========================================================================
def generate_card_front(card_meta):
    """
    生成卡牌正面框架：
    - 东方雅致温润底纸
    - 外层双线条框 + 四角如意回纹角饰
    - 顶部卡牌分类铭牌区 (带分类小印章)
    - 底部「悟堂审定」品牌印鉴水准线
    - 中间留白给程序渲染动态文本 (保留 100% 高对比净空区，中心仅有超淡禅意暗纹)
    """
    img = create_xuan_paper(CARD_W, CARD_H, base_color=card_meta["bg_color"])
    draw = ImageDraw.Draw(img)
    
    primary_color = card_meta["primary_color"]
    border_color = card_meta["border_color"]
    
    # 1. 外层边框
    margin = 18
    draw.rounded_rectangle([margin, margin, CARD_W - margin, CARD_H - margin], radius=8, outline=border_color, width=2)
    
    # 2. 内层细线边框
    in_margin = 25
    draw.rounded_rectangle([in_margin, in_margin, CARD_W - in_margin, CARD_H - in_margin], radius=6, outline=(*border_color[:3], 150), width=1)
    
    # 3. 四角古典角花
    draw_classical_corners(draw, in_margin, in_margin, CARD_W - in_margin, CARD_H - in_margin, primary_color, size=15)
    
    # 4. 顶部卡牌门类签条 (Cartouche Tag)
    tag_w, tag_h = 130, 28
    tag_x = (CARD_W - tag_w) // 2
    tag_y = in_margin + 12
    draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=14, fill=(255, 255, 255, 220), outline=border_color, width=1)
    
    # 顶部小印章
    seal_r = 14
    draw.rounded_rectangle([tag_x + 6, tag_y + 4, tag_x + 6 + seal_r * 2 - 6, tag_y + tag_h - 4], radius=3, fill=primary_color)
    font_s = get_font("simkai", 13)
    draw.text((tag_x + 10, tag_y + 6), card_meta["seal_char"], font=font_s, fill=(255, 255, 255))
    
    # 门类文字
    font_tag = get_font("simkai", 13)
    draw.text((tag_x + 36, tag_y + 6), card_meta["type_title"], font=font_tag, fill=PALETTE["ink_pure"])
    
    # 5. 背景极其淡雅的禅意暗纹 (仅 5% 不透明度，绝不干扰文字读取)
    if card_meta["theme_motif"] == "enso":
        enso_overlay = Image.new("RGBA", (CARD_W, CARD_H), (255, 255, 255, 0))
        edraw = ImageDraw.Draw(enso_overlay)
        draw_enso(edraw, CARD_W // 2, CARD_H // 2 + 10, 110, ink_color=primary_color)
        enso_overlay = enso_overlay.filter(ImageFilter.GaussianBlur(1))
        # 调整透明度为淡墨水印
        r, g, b, a = enso_overlay.split()
        a = a.point(lambda p: int(p * 0.08))
        enso_overlay.putalpha(a)
        img.paste(enso_overlay, (0, 0), enso_overlay)
    elif card_meta["theme_motif"] == "ripple":
        draw_concentric_zen_ripples(draw, CARD_W // 2, CARD_H // 2 + 30, 160, (*primary_color[:3], 20))
    elif card_meta["theme_motif"] == "mountain":
        draw_misty_mountains(draw, CARD_W, CARD_H, CARD_H - 140, primary_color)
    elif card_meta["theme_motif"] == "bamboo":
        draw_bamboo_branch(draw, CARD_W - in_margin - 35, CARD_H - 220, 150, (*primary_color[:3], 25))
    
    # 6. 中间程序动态内容安全框指示 (微弱内凹导线，提示程序正文排版边界)
    content_box = [in_margin + 16, tag_y + tag_h + 18, CARD_W - in_margin - 16, CARD_H - in_margin - 48]
    draw.rounded_rectangle(content_box, radius=4, outline=(*border_color[:3], 50), width=1)
    
    # 7. 底部品牌与出处水准线
    bot_y = CARD_H - in_margin - 24
    draw.line([(in_margin + 20, bot_y), (CARD_W - in_margin - 20, bot_y)], fill=(*border_color[:3], 120), width=1)
    
    # 底部微型印记
    draw_zen_seal(draw, in_margin + 36, bot_y - 2, 18, "悟", bg_color=PALETTE["vermilion"])
    font_bot = get_font("simkai", 11)
    draw.text((in_margin + 52, bot_y - 9), "悟堂 · 东方解忧处 · 澄怀观照", font=font_bot, fill=PALETTE["ink_light"])
    
    return img


# =========================================================================
# 核心生成器 2：卡牌背面禅意图腾 (Back Card Design)
# =========================================================================
def generate_card_back(card_meta):
    """
    生成卡牌背面：
    - 庄重深邃的东方禅宗视觉图腾
    - 双重回纹雅框与细密泥金边
    - 核心水墨禅圈 (Enso) / 涟漪 / 远岫 / 翠竹
    - 中心醒目朱砂篆字大印章
    - 古典竖排书法主题词或「今日一问」题跋
    - 沉静安宁，翻牌前带来强烈的冥想体验
    """
    img = create_xuan_paper(CARD_W, CARD_H, base_color=card_meta["bg_color"])
    draw = ImageDraw.Draw(img)
    
    primary_color = card_meta["primary_color"]
    border_color = card_meta["border_color"]
    
    # 1. 典雅双层外框
    m1 = 18
    draw.rounded_rectangle([m1, m1, CARD_W - m1, CARD_H - m1], radius=10, outline=border_color, width=2)
    m2 = 26
    draw.rounded_rectangle([m2, m2, CARD_W - m2, CARD_H - m2], radius=8, outline=(*border_color[:3], 160), width=1)
    
    # 2. 四角古典如意角花
    draw_classical_corners(draw, m2, m2, CARD_W - m2, CARD_H - m2, primary_color, size=18)
    
    # 3. 顶部题识
    font_top = get_font("simkai", 15)
    title_text = "悟 堂 · 今 日 觉 察"
    bbox = font_top.getbbox(title_text)
    tw = bbox[2] - bbox[0]
    draw.text(((CARD_W - tw) // 2, m2 + 24), title_text, font=font_top, fill=primary_color)
    
    # 顶部两颗泥金小圆点
    draw.ellipse([(CARD_W - tw) // 2 - 16, m2 + 30, (CARD_W - tw) // 2 - 12, m2 + 34], fill=PALETTE["gold_antique"])
    draw.ellipse([(CARD_W + tw) // 2 + 12, m2 + 30, (CARD_W + tw) // 2 + 16, m2 + 34], fill=PALETTE["gold_antique"])
    
    # 4. 中央图腾结构
    cx, cy = CARD_W // 2, CARD_H // 2 - 15
    
    # (a) 枯山水涟漪底衬
    draw_concentric_zen_ripples(draw, cx, cy, 145, PALETTE["border_sand"])
    
    # (b) 水墨禅圈 Enso
    draw_enso(draw, cx, cy, 105, ink_color=primary_color)
    
    # (c) 中心庄严朱砂印章
    draw_zen_seal(draw, cx, cy, 64, card_meta["seal_char"], bg_color=PALETTE["vermilion"])
    
    # (d) 意境主题图腾补充
    if card_meta["theme_motif"] == "mountain":
        draw_misty_mountains(draw, CARD_W, CARD_H, CARD_H - 180, primary_color)
    elif card_meta["theme_motif"] == "bamboo":
        draw_bamboo_branch(draw, m2 + 30, CARD_H - 260, 180, (*primary_color[:3], 120))
        draw_bamboo_branch(draw, CARD_W - m2 - 35, CARD_H - 230, 160, (*primary_color[:3], 100))
        
    # 5. 下方禅心箴言与操作提示
    font_sub = get_font("simkai", 17)
    sub_text = card_meta.get("back_motto", "静坐澄心 · 观照当下")
    s_bbox = font_sub.getbbox(sub_text)
    sw = s_bbox[2] - s_bbox[0]
    draw.text(((CARD_W - sw) // 2, cy + 130), sub_text, font=font_sub, fill=PALETTE["ink_pure"])
    
    # 细分隔短线
    draw.line([(CARD_W // 2 - 30, cy + 160), (CARD_W // 2 + 30, cy + 160)], fill=border_color, width=1)
    
    # 翻牌微按钮提示
    pill_w, pill_h = 140, 32
    pill_x = (CARD_W - pill_w) // 2
    pill_y = cy + 180
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=16, fill=(255, 255, 255, 230), outline=border_color, width=1)
    font_flip = get_font("simkai", 13)
    draw.text((pill_x + 22, pill_y + 8), "翻 开 见 智 慧  →", font=font_flip, fill=primary_color)
    
    # 6. 底款
    font_foot = get_font("simkai", 11)
    draw.text(((CARD_W - 140) // 2, CARD_H - m2 - 20), "让古老智慧，温和生活", font=font_foot, fill=PALETTE["ink_light"])
    
    return img


# =========================================================================
# 核心生成器 3：东方解忧笺（古典书笺）图案生成器 (Bookmarks / Slips)
# =========================================================================
def generate_zen_bookmark(bm_meta):
    """
    生成东方解忧笺（书笺）图案：
    - 420x900 比例雅致长条书笺
    - 顶部打孔及红色流苏挂绳孔
    - 双重回纹朱丝阑道
    - 宣纸 / 洒金 / 影青 / 水墨远岫不同风格质感
    - 底部或侧边题跋水墨插饰
    """
    img = create_xuan_paper(BOOKMARK_W, BOOKMARK_H, base_color=bm_meta["bg_color"])
    draw = ImageDraw.Draw(img)
    
    primary_color = bm_meta["primary_color"]
    line_color = bm_meta["line_color"]
    
    # 1. 顶部穿孔与挂穗位 (古典书签/书笺仪式感)
    hole_cx = BOOKMARK_W // 2
    hole_cy = 38
    # 铜扣 / 金圈打孔环
    draw.ellipse([hole_cx - 10, hole_cy - 10, hole_cx + 10, hole_cy + 10], outline=PALETTE["gold_antique"], width=2)
    draw.ellipse([hole_cx - 6, hole_cy - 6, hole_cx + 6, hole_cy + 6], fill=(230, 222, 210))
    # 象征性朱红丝绳挂绦
    draw.line([(hole_cx, hole_cy + 10), (hole_cx, hole_cy + 24)], fill=PALETTE["vermilion"], width=2)
    draw.polygon([(hole_cx - 4, hole_cy + 24), (hole_cx + 4, hole_cy + 24), (hole_cx, hole_cy + 32)], fill=PALETTE["vermilion"])
    
    # 2. 书笺双重雅框
    bx1, by1 = 20, 68
    bx2, by2 = BOOKMARK_W - 20, BOOKMARK_H - 24
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=6, outline=line_color, width=2)
    draw.rounded_rectangle([bx1 + 6, by1 + 6, bx2 - 6, by2 - 6], radius=4, outline=(*line_color[:3], 120), width=1)
    
    # 角花
    draw_classical_corners(draw, bx1 + 6, by1 + 6, bx2 - 6, by2 - 6, primary_color, size=14)
    
    # 3. 风格化背景特效
    style = bm_meta["style"]
    if style == "gold_fleck":
        # 洒金碎雪笺：点缀高雅小金箔碎屑
        random.seed(88)
        for _ in range(75):
            gx = random.randint(bx1 + 10, bx2 - 10)
            gy = random.randint(by1 + 10, by2 - 10)
            gr = random.randint(1, 3)
            draw.ellipse([gx, gy, gx + gr, gy + gr], fill=(212, 175, 95, random.randint(70, 160)))
            
    elif style == "ink_mountain":
        # 水墨远岫笺：底部烟波浩渺
        draw_misty_mountains(draw, BOOKMARK_W, BOOKMARK_H, BOOKMARK_H - 180, primary_color)
        
    elif style == "celadon_bamboo":
        # 影青竹韵笺：右侧雅竹虚心
        draw_bamboo_branch(draw, BOOKMARK_W - 50, BOOKMARK_H - 320, 240, (*primary_color[:3], 80))
        
    elif style == "cinnabar_seal":
        # 朱丝栏明清刻本笺：中间微红双栏竖线
        col_w = 42
        for col_i in range(5):
            cx_line = bx1 + 35 + col_i * col_w
            draw.line([(cx_line, by1 + 40), (cx_line, by2 - 60)], fill=(*PALETTE["vermilion"][:3], 45), width=1)
            
    elif style == "moonlit_pine":
        # 霁月松风笺：右上淡淡一轮明月与松枝
        draw.ellipse([BOOKMARK_W - 90, by1 + 25, BOOKMARK_W - 40, by1 + 75], outline=(*PALETTE["gold_antique"][:3], 90), width=1)
        draw.ellipse([BOOKMARK_W - 88, by1 + 27, BOOKMARK_W - 42, by1 + 73], fill=(255, 253, 245, 120))
        draw_bamboo_branch(draw, 50, BOOKMARK_H - 260, 200, (*primary_color[:3], 70))
        
    elif style == "ochre_sunset":
        # 晚照古铜笺：上下赭石晕染
        draw_concentric_zen_ripples(draw, BOOKMARK_W // 2, BOOKMARK_H // 2, 160, (*primary_color[:3], 25))
    elif style == "tea_sanctuary":
        # 云林茶隐笺：茶香清芬与温润水纹
        draw_concentric_zen_ripples(draw, BOOKMARK_W // 2, BOOKMARK_H - 180, 140, (*primary_color[:3], 35))
    elif style == "bamboo_shadow":
        # 修竹清风笺：挺秀墨竹
        draw_bamboo_branch(draw, BOOKMARK_W - 60, BOOKMARK_H - 360, 260, (*primary_color[:3], 95))
    elif style == "zen_stone":
        # 枯山静水笺：同心涟漪
        draw_concentric_zen_ripples(draw, BOOKMARK_W // 2, BOOKMARK_H - 160, 150, (*primary_color[:3], 45))
        
    # 4. 书笺顶端印标
    draw_zen_seal(draw, BOOKMARK_W // 2, by1 + 32, 28, "悟", bg_color=PALETTE["vermilion"])
    font_head = get_font("simkai", 13)
    draw.text((BOOKMARK_W // 2 - 58, by1 + 54), "悟 堂 · 东 方 解 忧 笺", font=font_head, fill=primary_color)
    
    # 5. 底部品牌与落款
    font_foot = get_font("simkai", 11)
    foot_text = "让古老智慧，用今天的人听得懂的方式活着"
    fb = font_foot.getbbox(foot_text)
    fw = fb[2] - fb[0]
    draw.text(((BOOKMARK_W - fw) // 2, by2 - 28), foot_text, font=font_foot, fill=PALETTE["ink_light"])
    
    return img


# =========================================================================
# 批量定义全套数据字典与生成清单
# =========================================================================

# 1. 核心三功能卡牌 + 通用觉察牌背
CORE_CARDS = [
    {
        "id": "card_universal",
        "name": "今日觉察·通用牌",
        "type_title": "今日觉察",
        "seal_char": "悟",
        "theme_motif": "enso",
        "bg_color": PALETTE["paper_base"],
        "primary_color": PALETTE["vermilion"],
        "border_color": PALETTE["border_gold"],
        "back_motto": "翻开今日一问 · 照见内心所向",
        "desc": "PRD 2.0 首页核心入口卡牌，支持翻转交互。"
    },
    {
        "id": "card_mindset",
        "name": "心境牌·看见自己",
        "type_title": "心境识别",
        "seal_char": "观",
        "theme_motif": "ripple",
        "bg_color": (252, 248, 243),
        "primary_color": PALETTE["vermilion"],
        "border_color": (224, 198, 185),
        "back_motto": "向内审视 · 先接纳真实的自己",
        "desc": "温和开放的反思提示卡，帮助用户识别并表达情绪。"
    },
    {
        "id": "card_wisdom",
        "name": "智慧牌·换个视角",
        "type_title": "东方智慧",
        "seal_char": "慧",
        "theme_motif": "enso",
        "bg_color": (250, 247, 238),
        "primary_color": PALETTE["gold_antique"],
        "border_color": PALETTE["border_gold"],
        "back_motto": "借古人千载智慧 · 照亮当下行迹",
        "desc": "经核验的国学经典出处、原文与现代白话解读。"
    },
    {
        "id": "card_action",
        "name": "行动牌·走出一步",
        "type_title": "轻量微行动",
        "seal_char": "行",
        "theme_motif": "bamboo",
        "bg_color": (246, 249, 246),
        "primary_color": PALETTE["pine_green"],
        "border_color": (195, 214, 202),
        "back_motto": "行者常至 · 从五分钟微小动作开始",
        "desc": "低门槛、可自主选择或跳过的 1-5 分钟微行动。"
    }
]

# 2. 数据库 6 大心性门类专属卡牌
DATABASE_CAT_CARDS = [
    {
        "id": "cat_cultivation",
        "name": "心性修养牌",
        "type_title": "心性修养",
        "seal_char": "修",
        "theme_motif": "enso",
        "bg_color": (250, 249, 246),
        "primary_color": PALETTE["ink_medium"],
        "border_color": PALETTE["border_sand"],
        "back_motto": "明心见性 · 致虚极而守静笃",
        "desc": "对应 500 条经典库之「心性修养」(120条)，讲求向内安顿与诚意正心。"
    },
    {
        "id": "cat_emotion",
        "name": "情绪调伏牌",
        "type_title": "情绪调伏",
        "seal_char": "定",
        "theme_motif": "mountain",
        "bg_color": (245, 248, 250),
        "primary_color": PALETTE["indigo_blue"],
        "border_color": (190, 208, 222),
        "back_motto": "定静安虑 · 烟消云散见晴川",
        "desc": "对应经典库之「情绪调伏」(85条)，化解焦虑内耗与意气难平。"
    },
    {
        "id": "cat_conduct",
        "name": "为人处世牌",
        "type_title": "为人处世",
        "seal_char": "和",
        "theme_motif": "bamboo",
        "bg_color": (246, 250, 247),
        "primary_color": PALETTE["bamboo_green"],
        "border_color": (198, 216, 204),
        "back_motto": "和光同尘 · 幽兰翠竹自生香",
        "desc": "对应经典库之「为人处世」(80条)，讲求中庸通达、方圆从容。"
    },
    {
        "id": "cat_relation",
        "name": "关系边界牌",
        "type_title": "关系与边界",
        "seal_char": "己",
        "theme_motif": "ripple",
        "bg_color": (252, 248, 244),
        "primary_color": PALETTE["ochre_brown"],
        "border_color": (224, 205, 190),
        "back_motto": "君子求己 · 疏朗适度两相安",
        "desc": "对应经典库之「关系与边界」(75条)，辨识讨好倾向、设立温和边界。"
    },
    {
        "id": "cat_choice",
        "name": "进退取舍牌",
        "type_title": "进退取舍",
        "seal_char": "止",
        "theme_motif": "enso",
        "bg_color": (251, 248, 240),
        "primary_color": PALETTE["gold_antique"],
        "border_color": PALETTE["border_gold"],
        "back_motto": "知足知止 · 进退从容天地宽",
        "desc": "对应经典库之「进退取舍」(65条)，取舍得失之间明察分寸。"
    },
    {
        "id": "cat_adversity",
        "name": "逆境成长牌",
        "type_title": "逆境与成长",
        "seal_char": "韧",
        "theme_motif": "mountain",
        "bg_color": (253, 246, 246),
        "primary_color": PALETTE["vermilion"],
        "border_color": (228, 196, 196),
        "back_motto": "履霜坚冰 · 经霜梅花发清幽",
        "desc": "对应经典库之「逆境与成长」(65条)，苦心励志、逆风破局。"
    }
]

# 3. 4 大解忧场景标签牌
SCENARIO_CARDS = [
    {
        "id": "scn_work",
        "name": "去班味牌",
        "type_title": "去班味 · 职场",
        "seal_char": "舒",
        "theme_motif": "mountain",
        "bg_color": (248, 247, 244),
        "primary_color": PALETTE["stone_gray"],
        "border_color": (214, 210, 204),
        "back_motto": "放下重担 · 厘清当下可控之步",
        "desc": "面向职场压力、被批评、过度内耗与方向迷茫。"
    },
    {
        "id": "scn_relation",
        "name": "松绑牌",
        "type_title": "松绑 · 人际",
        "seal_char": "宽",
        "theme_motif": "ripple",
        "bg_color": (252, 247, 242),
        "primary_color": PALETTE["ochre_brown"],
        "border_color": (226, 206, 192),
        "back_motto": "放下讨好 · 找回自己真实呼吸",
        "desc": "面向人际边界、不敢拒绝、家庭与伴侣期望压力。"
    },
    {
        "id": "scn_night",
        "name": "安住牌",
        "type_title": "安住 · 身心",
        "seal_char": "安",
        "theme_motif": "enso",
        "bg_color": (245, 248, 250),
        "primary_color": PALETTE["indigo_blue"],
        "border_color": (195, 210, 224),
        "back_motto": "歇心停思 · 允许万事留待明朝",
        "desc": "面向深夜反刍、思维停不下来、难以入眠焦虑。"
    },
    {
        "id": "scn_growth",
        "name": "破局牌",
        "type_title": "破局 · 选择",
        "seal_char": "破",
        "theme_motif": "bamboo",
        "bg_color": (247, 250, 246),
        "primary_color": PALETTE["pine_green"],
        "border_color": (200, 218, 205),
        "back_motto": "拆解重峦 · 迈出最小可能一步",
        "desc": "面向拖延停滞、完美主义恐惧与重大决策迟疑。"
    }
]

# 4. 东方解忧笺（6 款雅致书笺）
BOOKMARKS = [
    {
        "id": "bm_gold_fleck",
        "name": "冷金碎雪笺",
        "style": "gold_fleck",
        "bg_color": (252, 248, 238),
        "primary_color": PALETTE["gold_antique"],
        "line_color": PALETTE["border_gold"],
        "desc": "宣纸底色缀有点点细碎金箔，古雅华贵，适于保存哲思与金句。"
    },
    {
        "id": "bm_ink_mountain",
        "name": "澄心远岫笺",
        "style": "ink_mountain",
        "bg_color": (248, 247, 244),
        "primary_color": PALETTE["ink_medium"],
        "line_color": (210, 204, 195),
        "desc": "底部水墨烟雨远山淡影，空灵留白，诗情禅意。"
    },
    {
        "id": "bm_celadon_bamboo",
        "name": "青玉竹韵笺",
        "style": "celadon_bamboo",
        "bg_color": (246, 250, 248),
        "primary_color": PALETTE["bamboo_green"],
        "line_color": (195, 216, 205),
        "desc": "宋代影青瓷温润底色配虚心劲竹，清雅挺拔。"
    },
    {
        "id": "bm_cinnabar_seal",
        "name": "朱丝双阑笺",
        "style": "cinnabar_seal",
        "bg_color": (253, 249, 245),
        "primary_color": PALETTE["vermilion"],
        "line_color": (224, 185, 178),
        "desc": "仿明清木刻朱砂边栏与竖式信阑，正统文人书斋气息。"
    },
    {
        "id": "bm_moonlit_pine",
        "name": "松风霁月笺",
        "style": "moonlit_pine",
        "bg_color": (246, 248, 251),
        "primary_color": PALETTE["indigo_blue"],
        "line_color": (198, 212, 226),
        "desc": "明月高悬于苍松之上，幽深宁静，适于深夜歇心。"
    },
    {
        "id": "bm_ochre_sunset",
        "name": "落霞泥金笺",
        "style": "ochre_sunset",
        "bg_color": (252, 247, 240),
        "primary_color": PALETTE["ochre_brown"],
        "line_color": (222, 202, 186),
        "desc": "温厚暖赭泥金晕染渐变，时光沉淀感十足。"
    },
    {
        "id": "bm_tea_sanctuary",
        "name": "云林茶隐笺",
        "style": "tea_sanctuary",
        "bg_color": (252, 248, 240),
        "primary_color": (138, 92, 62),
        "line_color": (195, 165, 125),
        "desc": "青瓷茶盏与轻烟缭绕，烹茶候心，温润回甘。"
    },
    {
        "id": "bm_bamboo_shadow",
        "name": "修竹清风笺",
        "style": "bamboo_shadow",
        "bg_color": (247, 250, 247),
        "primary_color": PALETTE["pine_green"],
        "line_color": (185, 210, 192),
        "desc": "窗纱修竹疏影摇曳，虚心劲节，清风自来。"
    },
    {
        "id": "bm_zen_stone",
        "name": "枯山静水笺",
        "style": "zen_stone",
        "bg_color": (250, 248, 245),
        "primary_color": (90, 85, 80),
        "line_color": (205, 195, 182),
        "desc": "枯山水同心微澜与圆融禅石，风定水澄，照见本心。"
    }
]


def main():
    manifest = {
        "generated_at": "2026-10-18T20:45:00+08:00",
        "cards_total": len(CORE_CARDS) + len(DATABASE_CAT_CARDS) + len(SCENARIO_CARDS),
        "bookmarks_total": len(BOOKMARKS),
        "specs": {
            "card_resolution": f"{CARD_W}x{CARD_H}",
            "bookmark_resolution": f"{BOOKMARK_W}x{BOOKMARK_H}",
            "aspect_ratio_card": "2:3",
            "aspect_ratio_bookmark": "7:15",
            "aesthetic_style": "现代东方极简编辑设计 · 宣纸冷金朱砂墨韵"
        },
        "cards": [],
        "bookmarks": []
    }
    
    all_cards = CORE_CARDS + DATABASE_CAT_CARDS + SCENARIO_CARDS
    print(f"=== 开始批量生成悟堂东方禅意卡牌与书笺 (共 {len(all_cards)} 套卡牌 + {len(BOOKMARKS)} 套书笺) ===")
    
    # 1. 批量生成卡牌正反面
    for idx, card in enumerate(all_cards, 1):
        c_id = card["id"]
        front_path = os.path.join(CARD_DIR, "front", f"{c_id}_front.png")
        back_path = os.path.join(CARD_DIR, "back", f"{c_id}_back.png")
        
        # 生成正面与背面
        front_img = generate_card_front(card)
        back_img = generate_card_back(card)
        
        # 保存为轻量且保真的优化 PNG
        front_img.save(front_path, "PNG", optimize=True)
        back_img.save(back_path, "PNG", optimize=True)
        
        rel_front = f"assets/cards/front/{c_id}_front.png"
        rel_back = f"assets/cards/back/{c_id}_back.png"
        
        manifest["cards"].append({
            "id": c_id,
            "name": card["name"],
            "type_title": card["type_title"],
            "seal": card["seal_char"],
            "front_image": rel_front,
            "back_image": rel_back,
            "description": card["desc"]
        })
        print(f"[{idx}/{len(all_cards)}] 已生成卡牌: {card['name']} -> {rel_front} & {rel_back}")
        
    # 2. 批量生成书笺图案
    for idx, bm in enumerate(BOOKMARKS, 1):
        b_id = bm["id"]
        bm_path = os.path.join(BOOKMARK_DIR, f"{b_id}.png")
        bm_img = generate_zen_bookmark(bm)
        bm_img.save(bm_path, "PNG", optimize=True)
        
        rel_bm = f"assets/bookmarks/{b_id}.png"
        manifest["bookmarks"].append({
            "id": b_id,
            "name": bm["name"],
            "style": bm["style"],
            "image": rel_bm,
            "description": bm["desc"]
        })
        print(f"[{idx}/{len(BOOKMARKS)}] 已生成书笺: {bm['name']} -> {rel_bm}")
        
    # 3. 写入清单资产文件
    manifest_path = os.path.join(ROOT, "frontend", "assets", "cards_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] 资产清单已生成: {manifest_path}")

    # 4. 生成 Base64 内联字典包（确保单 HTML 离线无缝运行）
    import base64
    b64_dict = {"cards": {}, "bookmarks": {}}
    for c in manifest["cards"]:
        cid = c["id"]
        fp = os.path.join(CARD_DIR, "front", f"{cid}_front.png")
        bp = os.path.join(CARD_DIR, "back", f"{cid}_back.png")
        if os.path.exists(fp):
            with open(fp, "rb") as f:
                b64_dict["cards"][f"{cid}_front"] = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
        if os.path.exists(bp):
            with open(bp, "rb") as f:
                b64_dict["cards"][f"{cid}_back"] = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    for b in manifest["bookmarks"]:
        bid = b["id"]
        bmp = os.path.join(BOOKMARK_DIR, f"{bid}.png")
        if os.path.exists(bmp):
            with open(bmp, "rb") as f:
                b64_dict["bookmarks"][bid] = "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
                
    b64_path = os.path.join(ROOT, "frontend", "assets", "zen_card_assets.json")
    with open(b64_path, "w", encoding="utf-8") as f:
        json.dump(b64_dict, f)
    print(f"[OK] Base64离线资源包已生成: {b64_path} ({os.path.getsize(b64_path)/1024:.1f} KB)")
    print(f"     已生成卡牌正反面共 {len(all_cards) * 2} 张图 + 书笺 {len(BOOKMARKS)} 张图！")


if __name__ == "__main__":
    main()
