# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 先贤头像与印章小图标生成脚本
生成 16 位核心先贤的高清东方美学印章头像（512x512 PNG + Base64 字典）
风格：宣纸质感底色 + 双层回纹雅框 + 专属矿物印色色块 + 楷体大字书法印 + 篆隶名号签条
"""
import base64
import json
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "frontend", "assets", "avatars", "sages")
os.makedirs(OUT_DIR, exist_ok=True)

PAPER = (251, 247, 240)    # 宣纸白 #FBF7F0
INK_DARK = (43, 39, 36)    # 水墨浓黑 #2B2724
LINE_COLOR = (226, 218, 204) # 纸面暗线
GOLD_BORDER = (196, 160, 96) # 泥金色描边

SAGES = [
    {
        "id": "confucius", "keywords": ["孔子", "孔夫子", "论语"],
        "name": "孔子", "char": "丘", "title": "先师孔子",
        "era": "春秋·鲁", "color": (140, 58, 43),  # 朱砂红
        "motto": "君子求诸己 · 仁者爱人"
    },
    {
        "id": "laozi", "keywords": ["老子", "老聃", "道德经"],
        "name": "老子", "char": "聃", "title": "道家宗师",
        "era": "春秋·楚", "color": (43, 76, 95),   # 玄青黛蓝
        "motto": "道法自然 · 致虚守静"
    },
    {
        "id": "zhuangzi", "keywords": ["庄子", "庄周"],
        "name": "庄子", "char": "周", "title": "南华真人",
        "era": "战国·宋", "color": (74, 107, 79),  # 松竹清青
        "motto": "逍遥齐物 · 相忘江湖"
    },
    {
        "id": "mencius", "keywords": ["孟子", "孟轲"],
        "name": "孟子", "char": "轲", "title": "亚圣孟子",
        "era": "战国·邹", "color": (168, 97, 62),  # 赤褐陶铜
        "motto": "浩然之气 · 苦心励志"
    },
    {
        "id": "xunzi", "keywords": ["荀子", "荀卿", "荀况"],
        "name": "荀子", "char": "况", "title": "后圣荀子",
        "era": "战国·赵", "color": (90, 98, 117),  # 苍石青灰
        "motto": "锲而不舍 · 礼法修身"
    },
    {
        "id": "sushi", "keywords": ["苏轼", "苏东坡", "东坡居士"],
        "name": "苏轼", "char": "轼", "title": "东坡居士",
        "era": "北宋·眉州", "color": (176, 138, 74), # 赭石泥金
        "motto": "一蓑烟雨 · 也无风雨也无晴"
    },
    {
        "id": "wangyangming", "keywords": ["王阳明", "王守仁", "传习录"],
        "name": "王阳明", "char": "明", "title": "阳明先生",
        "era": "明代·余姚", "color": (158, 56, 43),  # 丹砂心学
        "motto": "知行合一 · 事上磨炼"
    },
    {
        "id": "zengguofan", "keywords": ["曾国藩", "曾文正"],
        "name": "曾国藩", "char": "藩", "title": "文正公",
        "era": "清代·湘乡", "color": (74, 85, 104),  # 刚毅铁墨
        "motto": "结硬寨打呆仗 · 莫问收获但问耕耘"
    },
    {
        "id": "taoyuanming", "keywords": ["陶渊明", "陶潜", "五柳先生"],
        "name": "陶渊明", "char": "渊", "title": "五柳先生",
        "era": "东晋·浔阳", "color": (181, 137, 0),  # 秋菊深黄
        "motto": "悠然南山 · 悟已往之不谏"
    },
    {
        "id": "wangwei", "keywords": ["王维", "王摩诘"],
        "name": "王维", "char": "维", "title": "诗佛右丞",
        "era": "盛唐·蒲州", "color": (63, 90, 122),  # 烟岚雨霁
        "motto": "行到水穷处 · 坐看云起时"
    },
    {
        "id": "simaqian", "keywords": ["司马迁", "太史公", "史记"],
        "name": "司马迁", "char": "迁", "title": "太史公",
        "era": "西汉·龙门", "color": (123, 82, 56),  # 简策古褐
        "motto": "发愤著书 · 究天人之际"
    },
    {
        "id": "hongyingming", "keywords": ["洪应明", "菜根谭"],
        "name": "洪应明", "char": "应", "title": "菜根道人",
        "era": "明代·新安", "color": (61, 107, 80),  # 菜根清绿
        "motto": "风来疏竹 · 宠辱不惊"
    },
    {
        "id": "jinying", "keywords": ["金缨", "格言联璧"],
        "name": "金缨", "char": "缨", "title": "联璧主人",
        "era": "清代·山阴", "color": (133, 90, 69),  # 晨钟古铜
        "motto": "静坐思己过 · 律己秋气处世春风"
    },
    {
        "id": "wangyongbin", "keywords": ["王永彬", "围炉夜话"],
        "name": "王永彬", "char": "彬", "title": "围炉居士",
        "era": "清代·枝江", "color": (150, 92, 56),  # 围炉温棕
        "motto": "逆境开拓心 · 安步当车"
    },
    {
        "id": "libai", "keywords": ["李白", "李太白"],
        "name": "李白", "char": "白", "title": "青莲居士",
        "era": "盛唐·绵州", "color": (77, 124, 138), # 青莲碧空
        "motto": "长风破浪 · 天生我材必有用"
    },
    {
        "id": "dufu", "keywords": ["杜甫", "杜工部"],
        "name": "杜甫", "char": "甫", "title": "诗圣工部",
        "era": "盛唐·巩县", "color": (58, 75, 92),   # 沉郁深黛
        "motto": "会当凌绝顶 · 一览众山小"
    },
    {
        "id": "default", "keywords": ["先贤", "古人"],
        "name": "悟堂先贤", "char": "悟", "title": "国学先哲",
        "era": "千古传灯", "color": (140, 58, 43),  # 悟堂朱砂
        "motto": "不说教先接住 · 借古人走眼前"
    }
]


def get_font(font_name, size):
    fonts = [
        os.path.join(r"C:\Windows\Fonts", font_name),
        os.path.join(r"C:\Windows\Fonts", "simkai.ttf"),
        os.path.join(r"C:\Windows\Fonts", "simsun.ttc"),
        os.path.join(r"C:\Windows\Fonts", "msyh.ttc"),
    ]
    for p in fonts:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def make_sage_avatar(sage, size=512):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 1. 宣纸背景圆角方框
    pad = 12
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=48, fill=PAPER, outline=LINE_COLOR, width=2)
    # 细回纹内框
    d.rounded_rectangle([pad + 10, pad + 10, size - pad - 10, size - pad - 10], radius=40, outline=LINE_COLOR, width=1)

    # 2. 核心先贤印章主体 (上部大印章)
    cx, cy = size // 2, int(size * 0.44)
    r = int(size * 0.32)

    # 印章外圈微金光 / 雅边
    d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=GOLD_BORDER)
    # 印章底色（先贤专属矿物色）
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=sage["color"])
    # 印章内白线（传统汉印白文/朱文边框感）
    d.ellipse([cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12], outline=(255, 255, 255, 180), width=3)

    # 3. 印章核心大字（书法楷体单字）
    font_char = get_font("simkai.ttf", int(r * 1.15))
    ch = sage["char"]
    # 计算文字居中
    bbox = d.textbbox((0, 0), ch, font=font_char)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = cx - tw // 2 - bbox[0]
    ty = cy - th // 2 - bbox[1]
    # 印文字用宣纸白，微微透出底色厚重感
    d.text((tx, ty), ch, font=font_char, fill=(255, 255, 255, 245))

    # 4. 底部先贤名号签条（仿宋体/楷体）
    tag_w = int(size * 0.65)
    tag_h = 56
    tag_x = (size - tag_w) // 2
    tag_y = int(size * 0.81)

    d.rounded_rectangle([tag_x, tag_y, tag_x + tag_w, tag_y + tag_h], radius=12, fill=(255, 255, 255, 220), outline=sage["color"], width=2)
    # 小红印泥点缀
    d.ellipse([tag_x + 10, tag_y + 18, tag_x + 28, tag_y + 36], fill=sage["color"])

    font_title = get_font("simsun.ttc", 26)
    title_text = f"{sage['title']}"
    tb = d.textbbox((0, 0), title_text, font=font_title)
    ttw, tth = tb[2] - tb[0], tb[3] - tb[1]
    ttx = tag_x + (tag_w - ttw) // 2 + 10
    tty = tag_y + (tag_h - tth) // 2 - tb[1]
    d.text((ttx, tty), title_text, font=font_title, fill=INK_DARK)

    return img


def main():
    b64_dict = {}
    print(f"[start] 开始生成 {len(SAGES)} 位先贤东方美学头像图标...")
    for s in SAGES:
        img = make_sage_avatar(s)
        # 1. 保存 512x512 高清 PNG
        png_path = os.path.join(OUT_DIR, f"{s['id']}.png")
        img.save(png_path, "PNG")

        # 2. 生成适合内联的 96x96 小尺寸 WebP/PNG Base64（保持单文件极速加载）
        small_img = img.resize((96, 96), Image.Resampling.LANCZOS)
        import io
        buf = io.BytesIO()
        small_img.save(buf, format="PNG", optimize=True)
        b64_str = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
        b64_dict[s["id"]] = {
            "name": s["name"],
            "title": s["title"],
            "era": s["era"],
            "motto": s["motto"],
            "color": f"rgb({s['color'][0]}, {s['color'][1]}, {s['color'][2]})",
            "b64": b64_str,
            "keywords": s["keywords"]
        }
        print(f"  [ok] {s['name']} ({s['title']}) → {s['id']}.png")

    # 3. 输出汇总 json 供前端快速索引和内联
    json_path = os.path.join(ROOT, "frontend", "assets", "sage_avatars.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(b64_dict, f, ensure_ascii=False, indent=2)

    print(f"[done] 先贤头像已全部生成完成！输出目录：{OUT_DIR}")
    print(f"       数据索引已生成：{json_path}")


if __name__ == "__main__":
    main()
