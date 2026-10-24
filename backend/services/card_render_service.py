# -*- coding: utf-8 -*-
"""
悟堂 · 东方解忧卡牌渲染与打印导出服务
工业级印刷标准：
- 尺寸：标准 TCG 对战卡尺寸 63mm x 88mm + 2mm 出血线 = 67mm x 92mm
- 分辨率：300 DPI (791 x 1087 像素)
- 元素：正面（意境/定心偈/专属印鉴/角标裁切线）、背面（经典出处/今日小事）、专色烫金遮罩层 (Foil Mask)
"""
import io
import os
import zipfile
import json
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont

FONTS_DIR = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")

def get_font(name: str, size: int):
    candidates = [
        os.path.join(FONTS_DIR, name),
        os.path.join(FONTS_DIR, "simsun.ttc"),
        os.path.join(FONTS_DIR, "msyh.ttc"),
        os.path.join(FONTS_DIR, "simhei.ttf"),
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()

def wrap_text(text: str, max_chars_per_line: int) -> list:
    """按字符数折行（支持中文标点与英文折行）"""
    lines = []
    current = ""
    for char in text:
        if char == "\n":
            lines.append(current)
            current = ""
            continue
        current += char
        if len(current) >= max_chars_per_line:
            lines.append(current)
            current = ""
    if current:
        lines.append(current)
    return lines

class CardRenderService:
    WIDTH = 791   # 67mm @ 300 DPI
    HEIGHT = 1087 # 92mm @ 300 DPI
    BLEED = 24    # 2mm @ 300 DPI

    SCHOOL_THEMES = {
        "confucianism": {
            "name": "儒学·入世修身",
            "master": "孔子",
            "primary": (142, 41, 39),      # 朱砂深红 #8E2927
            "secondary": (159, 116, 48),   # 雅金 #9F7430
            "bg": (248, 244, 235),         # 宣纸暖白 #F8F4EB
            "inner_bg": (253, 251, 247),
            "seal_text": "心安",
        },
        "daoism": {
            "name": "道学·顺应自然",
            "master": "老子",
            "primary": (43, 76, 95),       # 玄水靛青 #2B4C5F
            "secondary": (58, 109, 79),    # 松针绿 #3A6D4F
            "bg": (244, 247, 245),         # 青润宣白
            "inner_bg": (250, 252, 251),
            "seal_text": "道法自然",
        },
        "buddhism": {
            "name": "释学·观照自在",
            "master": "释迦牟尼",
            "primary": (181, 137, 0),      # 佛辉澄金 #B58900
            "secondary": (150, 60, 45),    # 赭石红
            "bg": (250, 247, 240),         # 佛金暖白
            "inner_bg": (255, 253, 249),
            "seal_text": "自在",
        },
        "symposium": {
            "name": "三圣圆桌·圆融会诊",
            "master": "三圣合参",
            "primary": (118, 55, 98),      # 紫金华光
            "secondary": (159, 116, 48),
            "bg": (248, 245, 242),
            "inner_bg": (253, 251, 249),
            "seal_text": "会心",
        }
    }

    def _draw_crop_marks(self, draw: ImageDraw.ImageDraw):
        """绘制印刷标准十字裁切线"""
        b = self.BLEED
        w, h = self.WIDTH, self.HEIGHT
        color = (180, 180, 180)
        # 左上
        draw.line([(b, 0), (b, b - 6)], fill=color, width=1)
        draw.line([(0, b), (b - 6, b)], fill=color, width=1)
        # 右上
        draw.line([(w - b, 0), (w - b, b - 6)], fill=color, width=1)
        draw.line([(w, b), (w - b + 6, b)], fill=color, width=1)
        # 左下
        draw.line([(b, h), (b, h - b + 6)], fill=color, width=1)
        draw.line([(0, h - b), (b - 6, h - b)], fill=color, width=1)
        # 右下
        draw.line([(w - b, h), (w - b, h - b + 6)], fill=color, width=1)
        draw.line([(w, h - b), (w - b + 6, h - b)], fill=color, width=1)

    def _draw_borders(self, draw: ImageDraw.ImageDraw, primary: tuple, secondary: tuple):
        """绘制古典回纹边框与金线"""
        b = self.BLEED
        margin = b + 12
        inner_m = margin + 14

        # 外框（深色细线）
        draw.rectangle([margin, margin, self.WIDTH - margin, self.HEIGHT - margin], outline=primary, width=2)
        # 内框（雅金色细线）
        draw.rectangle([inner_m, inner_m, self.WIDTH - inner_m, self.HEIGHT - inner_m], outline=secondary, width=1)

        # 四角如意云头微饰
        for x, y in [
            (inner_m, inner_m),
            (self.WIDTH - inner_m, inner_m),
            (inner_m, self.HEIGHT - inner_m),
            (self.WIDTH - inner_m, self.HEIGHT - inner_m),
        ]:
            draw.rectangle([x - 5, y - 5, x + 5, y + 5], fill=secondary)

    def _draw_seal(self, draw: ImageDraw.ImageDraw, x: int, y: int, text: str):
        """绘制朱砂小印章"""
        size = 54
        draw.rectangle([x, y, x + size, y + size], fill=(168, 48, 42), outline=(130, 30, 25), width=2)
        font = get_font("simsun.ttc", 20)
        t1, t2 = text[:2], text[2:4] if len(text) >= 4 else text[2:]
        draw.text((x + 7, y + 6), t1, fill=(255, 245, 235), font=font)
        if t2:
            draw.text((x + 7, y + 28), t2, fill=(255, 245, 235), font=font)

    def render_card_front(self, data: Dict[str, Any]) -> Image.Image:
        """渲染 300 DPI 打印级卡牌正面（意境与定心）"""
        school_key = data.get("school", "confucianism")
        theme = self.SCHOOL_THEMES.get(school_key, self.SCHOOL_THEMES["confucianism"])

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), theme["bg"])
        draw = ImageDraw.Draw(img)

        # 1. 裁切线与边框
        self._draw_crop_marks(draw)
        self._draw_borders(draw, theme["primary"], theme["secondary"])

        # 2. 顶栏标识 (流派与全球唯一编号)
        top_y = self.BLEED + 32
        font_tag = get_font("simsun.ttc", 22)
        font_num = get_font("msyh.ttc", 20)
        
        school_title = f"【悟堂·{theme['name']}】"
        draw.text((self.BLEED + 32, top_y), school_title, fill=theme["primary"], font=font_tag)

        card_no = data.get("card_number") or f"WU-DAO-{data.get('card_id', '001')}"
        draw.text((self.WIDTH - self.BLEED - 32 - len(card_no) * 11, top_y + 1), card_no, fill=(120, 115, 110), font=font_num)

        # 3. 核心法门（2字书法题名）
        card_name = data.get("name", "明德")
        font_big = get_font("simsun.ttc", 92)
        name_str = f"【 {card_name} 】" if len(card_name) <= 2 else f"【{card_name}】"
        draw.text((self.WIDTH // 2 - (len(name_str) * 46), 180), name_str, fill=theme["primary"], font=font_big)

        # 4. 导师与法门定位
        master_name = data.get("master", theme["master"])
        motto = data.get("master_motto", "立足东方智慧 · 照亮人生之路")
        font_sub = get_font("msyh.ttc", 26)
        sub_str = f"先贤 {master_name} 寄语 ｜ {motto}"
        draw.text((self.WIDTH // 2 - (len(sub_str) * 13), 290), sub_str, fill=theme["secondary"], font=font_sub)

        # 5. 装饰横线
        line_y = 335
        draw.line([(self.WIDTH // 2 - 160, line_y), (self.WIDTH // 2 + 160, line_y)], fill=theme["secondary"], width=1)
        draw.rectangle([(self.WIDTH // 2 - 4, line_y - 4), (self.WIDTH // 2 + 4, line_y + 4)], fill=theme["primary"])

        # 6. 中央核心定心偈 (金句)
        aphorism = data.get("aphorism") or data.get("core") or "君子求诸己，万般皆因行未至。"
        font_aph = get_font("simsun.ttc", 36)
        aph_lines = wrap_text(aphorism, 14)
        aph_y = 420
        for line in aph_lines:
            draw.text((self.WIDTH // 2 - (len(line) * 18), aph_y), line, fill=(34, 31, 27), font=font_aph)
            aph_y += 54

        # 7. 英文定心箴言 (增强现代感与出海传播度)
        eng_mantra = data.get("english_mantra") or "Self-discipline and virtue bring enduring inner peace."
        font_eng = get_font("msyh.ttc", 20)
        eng_lines = wrap_text(eng_mantra, 42)
        eng_y = max(aph_y + 20, 560)
        for line in eng_lines:
            draw.text((self.WIDTH // 2 - (len(line) * 5), eng_y), line, fill=(120, 110, 100), font=font_eng)
            eng_y += 28

        # 8. 意境插画描述 / 象征印记
        draw.rectangle([self.WIDTH // 2 - 180, 680, self.WIDTH // 2 + 180, 830], outline=(220, 215, 205), width=1)
        scene_desc = data.get("scene") or f"水墨意境：{theme['name']}，静水流深，古木生青，见心如镜。"
        font_scene = get_font("simsun.ttc", 20)
        scene_lines = wrap_text(scene_desc, 22)[:3]
        s_y = 705
        for line in scene_lines:
            draw.text((self.WIDTH // 2 - (len(line) * 10), s_y), line, fill=(100, 95, 90), font=font_scene)
            s_y += 34

        # 9. 底栏信息 (节令、署名、印章)
        bottom_y = self.HEIGHT - self.BLEED - 110
        font_bot = get_font("simsun.ttc", 24)
        lunar_date = data.get("lunar_date", "丙午年 · 霜降")
        user_name = data.get("user_nickname", "朋友")

        draw.text((self.BLEED + 44, bottom_y), f"节令：{lunar_date}", fill=(80, 75, 70), font=font_bot)
        draw.text((self.BLEED + 44, bottom_y + 36), f"使用者：{user_name}", fill=theme["primary"], font=font_bot)

        # 朱砂印章
        self._draw_seal(draw, self.WIDTH - self.BLEED - 100, bottom_y - 8, theme["seal_text"])

        return img

    def render_card_back(self, data: Dict[str, Any]) -> Image.Image:
        """渲染 300 DPI 打印级卡牌背面（经典出处与今日小事）"""
        school_key = data.get("school", "confucianism")
        theme = self.SCHOOL_THEMES.get(school_key, self.SCHOOL_THEMES["confucianism"])

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), theme["inner_bg"])
        draw = ImageDraw.Draw(img)

        # 1. 裁切线与边框
        self._draw_crop_marks(draw)
        self._draw_borders(draw, theme["primary"], theme["secondary"])

        # 2. 背面标题
        top_y = self.BLEED + 32
        font_tag = get_font("simsun.ttc", 22)
        draw.text((self.BLEED + 32, top_y), "【解忧笺 · 经典与行动】", fill=theme["primary"], font=font_tag)

        # 3. 心事栏（默认渲染中性文案；仅 include_personal_note=True 显式开启时才渲染个人心事，
        #    个人留念版正式开放前还需：前端显式勾选 + 不可撤回警示 + 九类 PII 扫描）
        draw.rectangle([self.BLEED + 30, 110, self.WIDTH - self.BLEED - 30, 220], fill=(245, 241, 232), outline=(230, 224, 212))
        font_sec = get_font("simsun.ttc", 24)
        draw.text((self.BLEED + 44, 122), "【今日心事 · 一句安放】", fill=theme["secondary"], font=font_sec)
        
        if data.get("include_personal_note"):
            user_problem = data.get("user_statement") or ""
        else:
            user_problem = "有些事压在心头，想找个安静的角落理一理。"
        font_txt = get_font("msyh.ttc", 21)
        prob_lines = wrap_text(user_problem, 26)[:2]
        p_y = 158
        for line in prob_lines:
            draw.text((self.BLEED + 46, p_y), line, fill=(60, 55, 50), font=font_txt)
            p_y += 28

        # 4. 先贤原典 (引用)
        classic_box_y = 245
        draw.rectangle([self.BLEED + 30, classic_box_y, self.WIDTH - self.BLEED - 30, 570], fill=(255, 255, 255), outline=theme["secondary"])
        draw.text((self.BLEED + 44, classic_box_y + 16), "【先贤引典 · 原文与白话】", fill=theme["primary"], font=font_sec)

        book_info = data.get("classic_source") or "《论语·卫灵公》（春秋·孔子）"
        draw.text((self.BLEED + 44, classic_box_y + 50), book_info, fill=theme["secondary"], font=get_font("msyh.ttc", 20))

        quote = data.get("quote") or "君子求诸己，小人求诸人。"
        font_quote = get_font("simsun.ttc", 28)
        q_lines = wrap_text(f"「{quote}」", 20)
        q_y = classic_box_y + 90
        for line in q_lines:
            draw.text((self.BLEED + 48, q_y), line, fill=(30, 28, 25), font=font_quote)
            q_y += 38

        interpretation = data.get("interpretation") or "遇到不顺先看自己能做什么，而不是先怪外界。把力气收回到自己身上，是瓦解内耗的唯一解药。"
        font_interp = get_font("msyh.ttc", 21)
        interp_lines = wrap_text(interpretation, 25)[:4]
        i_y = q_y + 16
        for line in interp_lines:
            draw.text((self.BLEED + 48, i_y), line, fill=(70, 65, 60), font=font_interp)
            i_y += 30

        # 5. 今日 5 分钟微行动
        action_y = 595
        draw.rectangle([self.BLEED + 30, action_y, self.WIDTH - self.BLEED - 30, 890], fill=(245, 248, 245), outline=(200, 220, 205))
        draw.text((self.BLEED + 44, action_y + 18), "【今日小事 · 5 分钟微行动】", fill=(45, 100, 60), font=font_sec)

        action_title = data.get("action_title") or "静坐调息，记录眼前3件可控之事"
        draw.text((self.BLEED + 46, action_y + 54), f"● {action_title}", fill=(30, 30, 30), font=get_font("msyh.ttc", 23))

        action_steps = data.get("action_steps") or [
            "停下手中的屏幕与辩解，合上双眼，做三次深长的腹式深呼吸。",
            "拿出一支笔，写下一件此刻力所能及的小事并立即动手完成。",
            "完成后在心里对自己说一句定心的话，安然进入梦乡。"
        ]
        s_y = action_y + 96
        font_step = get_font("msyh.ttc", 21)
        for idx, step in enumerate(action_steps[:3], 1):
            lines = wrap_text(f"{idx}. {step}", 25)
            for l in lines:
                draw.text((self.BLEED + 46, s_y), l, fill=(65, 60, 55), font=font_step)
                s_y += 30
            s_y += 6

        # 6. 底栏防伪溯源码提示
        draw.text((self.BLEED + 44, self.HEIGHT - self.BLEED - 70), "悟堂·东方解忧处 ｜ 印刷专用母版", fill=(130, 125, 120), font=get_font("simsun.ttc", 20))
        draw.text((self.BLEED + 44, self.HEIGHT - self.BLEED - 40), "Authentic Eastern Wisdom Relief Card · 300 DPI TCG Ready", fill=(160, 155, 150), font=get_font("msyh.ttc", 17))

        return img

    def render_foil_mask(self, data: Dict[str, Any]) -> Image.Image:
        """生成实体印刷烫金工艺专色遮罩层 (Foil Mask, 纯黑遮罩即烫金区域)"""
        mask = Image.new("RGB", (self.WIDTH, self.HEIGHT), (255, 255, 255))
        draw = ImageDraw.Draw(mask)

        # 烫金内边框与四角
        b = self.BLEED
        inner_m = b + 26
        draw.rectangle([inner_m, inner_m, self.WIDTH - inner_m, self.HEIGHT - inner_m], outline=(0, 0, 0), width=2)
        for x, y in [
            (inner_m, inner_m),
            (self.WIDTH - inner_m, inner_m),
            (inner_m, self.HEIGHT - inner_m),
            (self.WIDTH - inner_m, self.HEIGHT - inner_m),
        ]:
            draw.rectangle([x - 7, y - 7, x + 7, y + 7], fill=(0, 0, 0))

        # 烫金卡牌名称
        card_name = data.get("name", "明德")
        font_big = get_font("simsun.ttc", 92)
        name_str = f"【 {card_name} 】" if len(card_name) <= 2 else f"【{card_name}】"
        draw.text((self.WIDTH // 2 - (len(name_str) * 46), 180), name_str, fill=(0, 0, 0), font=font_big)

        # 烫金小横线
        line_y = 335
        draw.line([(self.WIDTH // 2 - 160, line_y), (self.WIDTH // 2 + 160, line_y)], fill=(0, 0, 0), width=2)
        draw.rectangle([(self.WIDTH // 2 - 5, line_y - 5), (self.WIDTH // 2 + 5, line_y + 5)], fill=(0, 0, 0))

        return mask

    def create_print_pack(self, data: Dict[str, Any]) -> bytes:
        """生成包含正、反、烫金遮罩与规格说明的 ZIP 打印包"""
        front_img = self.render_card_front(data)
        back_img = self.render_card_back(data)
        foil_img = self.render_foil_mask(data)

        # 内存中打包
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. 正面 300 DPI
            f_buf = io.BytesIO()
            front_img.save(f_buf, format="PNG", dpi=(300, 300))
            zf.writestr("01_卡牌正面_300DPI_含出血.png", f_buf.getvalue())

            # 2. 背面 300 DPI
            b_buf = io.BytesIO()
            back_img.save(b_buf, format="PNG", dpi=(300, 300))
            zf.writestr("02_卡牌背面_300DPI_含出血.png", b_buf.getvalue())

            # 3. 烫金工艺遮罩 (Foil Mask)
            m_buf = io.BytesIO()
            foil_img.save(m_buf, format="PNG", dpi=(300, 300))
            zf.writestr("03_专色烫哑金遮罩_FoilMask.png", m_buf.getvalue())

            # 4. 打印店操作指南与参数台账
            readme = f"""# 悟堂 · 东方解忧实体卡牌打印指南

- 最终成品裁切尺寸：63mm x 88mm (标准国际 TCG 卡牌规格)
- 画布含出血尺寸：67mm x 92mm (四周各 2mm 出血，已绘制裁切基准线)
- 分辨率：300 DPI (791 x 1087 像素)
- 推荐纸张：350g 触感特种纸 / 300g 宣纸双面对裱 / 350g 进口白芯铜版纸
- 推荐工艺：正面局部烫哑金（请使用 03_专色烫哑金遮罩_FoilMask.png 出菲林板）
- 适用卡套：标准 65mm x 90mm TCG 卡套、卡砖或集卡册

本文件由「悟堂·东方智慧问答解惑与专属解忧卡牌系统」自动生成。
"""
            zf.writestr("印刷店下单说明_README.txt", readme.encode("utf-8"))

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

card_render_service = CardRenderService()
