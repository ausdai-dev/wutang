# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    c = f.read()

reps = [
    ('👑 主理人特权 · 全量卡牌库', '主理人特权 · 全量卡牌库'),
    ('⭐ 我的收藏', '我的收藏'),
    ('👑 百八常道库 (108)', '百八常道库 (108)'),
    ('🖼️ 觉察牌画廊 (96)', '觉察牌画廊 (96)'),
    ('🖼 觉察牌画廊 (96)', '觉察牌画廊 (96)'),
    ('📦 主题卡牌包 (6)', '主题卡牌包 (6)'),
    ('🔄 刷新珍藏', '刷新珍藏'),
    ("'卡牌人生 · 我的收藏与全量卡牌库 👑'", "'卡牌人生 · 我的收藏与全量卡牌库'"),
    ('<div style="font-size:36px;margin-bottom:8px;">🎴</div>', '<div style="font-size:14px;color:var(--color-primary);font-weight:700;margin-bottom:8px;">【虚堂待悟】</div>'),
    ('前往解忧参悟抽牌 ✨', '前往解忧参悟抽牌'),
    ('title="移出珍藏">★ 移出</button>', 'title="移出珍藏">移出</button>'),
    ("onclick=\"toggleFavoriteCard('' + esc(cid) + '')\">★ 移出</button>", "onclick=\"toggleFavoriteCard('' + esc(cid) + '')\">移出</button>"),
    ("onclick=\"toggleFavoriteCard('\\' + esc(cid) + '\\')\">★ 移出</button>", "onclick=\"toggleFavoriteCard('\\' + esc(cid) + '\\')\">移出</button>"),
    ("★ 移出", "移出"),
]

for o, n in reps:
    if o in c:
        c = c.replace(o, n)
        print(f"Replaced: {o[:25]} -> {n[:25]}")

with open('frontend/_template.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Updated template.")
