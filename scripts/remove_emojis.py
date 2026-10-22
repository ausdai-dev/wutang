# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Exact text replacements to preserve exact formatting and eliminate emojis:
replacements = [
    # Top bar & Header
    ('<span style="font-size:12px;margin-right:2px;">👑</span> 主理人', '主理人'),
    ('<span class="bgm-panel-title">🌿 悟堂 · 禅意背景音</span>', '<span class="bgm-panel-title">悟堂 · 禅意背景音</span>'),
    ('<span id="bgmVolIcon" style="cursor:pointer;user-select:none;" title="静音切换">🔉</span>', '<span id="bgmVolIcon" style="cursor:pointer;user-select:none;font-size:12px;" title="静音切换">音量</span>'),
    ('<span>🍵 遇事不决？抽取今日东方锦囊/禅签 →</span>', '<span>遇事不决？抽取今日东方锦囊/禅签 →</span>'),
    ('<span>🌿 延长静观 +5秒</span>', '<span>延长静观 +5秒</span>'),
    ('<span>提前揭晓 ➔</span>', '<span>提前揭晓 →</span>'),
    ('<span>✓</span> 梳理完成', '<span class="status-icon">·</span> 梳理完成'),

    # Hero card & Liberation card
    ('<span>🖼️ 借境观心 · 契合心象画卷</span>', '<span>借境观心 · 契合心象画卷</span>'),
    ('<span>🖼 借境观心 · 契合心象画卷</span>', '<span>借境观心 · 契合心象画卷</span>'),
    ('<div class="resonant-card-img-hint">✨ 点击赏析 848x1264 原画 / 3D 翻转</div>', '<div class="resonant-card-img-hint">点击赏析 848x1264 原画 / 3D 翻转</div>'),
    ('<span>✍️ 以此牌写觉察日记</span>', '<span>以此牌写觉察日记</span>'),
    ('<span>✍ 以此牌写觉察日记</span>', '<span>以此牌写觉察日记</span>'),
    ('<span>🔍 在 96 画廊中研读</span>', '<span>在 96 画廊中研读</span>'),
    ('<span>🔍 3D 翻转 / 在 96 画廊中研读</span>', '<span>在 96 画廊中研读 / 翻转赏析</span>'),
    ('<span>🔄 翻转卡面</span>', '<span>翻转卡面</span>'),
    ('<span>🖨️ 导出 300DPI 实体打印包 (送印级)</span>', '<span>导出 300DPI 实体打印包 (送印级)</span>'),
    ('<span>🖨 导出 300DPI 实体打印包 (送印级)</span>', '<span>导出 300DPI 实体打印包 (送印级)</span>'),
    ('<span>📱 保存手机高清壁纸</span>', '<span>保存手机高清壁纸</span>'),
    ('<span>📜 珍藏入册</span>', '<span>珍藏入册</span>'),

    # Mood chips
    ('<div class="mood-chip" data-mood="calm"><span>🌿</span> 平静从容</div>', '<div class="mood-chip" data-mood="calm">平静从容</div>'),
    ('<div class="mood-chip" data-mood="joy"><span>✨</span> 充实欣喜</div>', '<div class="mood-chip" data-mood="joy">充实欣喜</div>'),
    ('<div class="mood-chip" data-mood="tired"><span>🍂</span> 疲惫有些透支</div>', '<div class="mood-chip" data-mood="tired">疲惫透支</div>'),
    ('<div class="mood-chip" data-mood="anxious"><span>🌪️</span> 焦虑心慌</div>', '<div class="mood-chip" data-mood="anxious">焦虑心慌</div>'),
    ('<div class="mood-chip" data-mood="anxious"><span>🌪</span> 焦虑心慌</div>', '<div class="mood-chip" data-mood="anxious">焦虑心慌</div>'),
    ('<div class="mood-chip" data-mood="frustrated"><span>🔥</span> 烦躁窝火</div>', '<div class="mood-chip" data-mood="frustrated">烦躁窝火</div>'),
    ('<div class="mood-chip" data-mood="sad"><span>🌧️</span> 沮丧失落</div>', '<div class="mood-chip" data-mood="sad">沮丧失落</div>'),
    ('<div class="mood-chip" data-mood="sad"><span>🌧</span> 沮丧失落</div>', '<div class="mood-chip" data-mood="sad">沮丧失落</div>'),
    ('<div class="mood-chip" data-mood="overthinking"><span>🌀</span> 内耗反刍</div>', '<div class="mood-chip" data-mood="overthinking">内耗反刍</div>'),
    ('<div class="mood-chip" data-mood="relieved"><span>☁️</span> 释怀看开</div>', '<div class="mood-chip" data-mood="relieved">释怀看开</div>'),
    ('<div class="mood-chip" data-mood="relieved"><span>☁</span> 释怀看开</div>', '<div class="mood-chip" data-mood="relieved">释怀看开</div>'),

    # Energy pills
    ('<div class="level-pill" data-level="high">充沛 ⚡</div>', '<div class="level-pill" data-level="high">充沛</div>'),
    ('<div class="level-pill active" data-level="normal">一般 🔋</div>', '<div class="level-pill active" data-level="normal">一般</div>'),
    ('<div class="level-pill" data-level="low">疲惫 🪫</div>', '<div class="level-pill" data-level="low">疲惫</div>'),
    ('<div class="level-pill" data-level="drained">透支 💤</div>', '<div class="level-pill" data-level="drained">透支</div>'),

    # Growth & Wellbeing
    ('<span style="font-size:20px;">🍵</span>', '<span class="badge ok" style="font-size:12px;">心境已安</span>'),
    ('<button class="btn" id="btnAiOrganizeJournal">🌿 AI 结构化梳理心绪</button>', '<button class="btn" id="btnAiOrganizeJournal">AI 结构化梳理心绪</button>'),
    ('<span style="font-size:18px;">🌱</span>', '<span class="badge" style="background:var(--color-primary-light);color:var(--color-primary);font-size:11.5px;">微功课</span>'),
    ('<button class="btn sm secondary" data-action-status="completed">已做到了 🌿</button>', '<button class="btn sm secondary" data-action-status="completed">已做到</button>'),
    ('<button class="btn sm secondary" data-action-status="partial">做了一部分 ✨</button>', '<button class="btn sm secondary" data-action-status="partial">做了一部分</button>'),
    ('<button class="btn sm secondary" data-action-status="unsuitable">方法不适合我 🔄</button>', '<button class="btn sm secondary" data-action-status="unsuitable">方法不适合我</button>'),
    ('<span>📜</span> 本周觉察回顾摘要', '本周觉察回顾摘要'),
    ('🧭 情绪触发场景归纳', '情绪触发场景归纳'),
    ('任务 ➔ 容易', '任务 → 容易'),
    ('挑错 ➔ 容易', '挑错 → 容易'),
    ('🌱 当前成长主题：关系边界', '当前成长主题：关系边界'),
    ('<span style="font-size:24px;">⚖️</span>', '<span class="badge" style="background:var(--color-gold-bg);color:var(--color-gold);border:1px solid var(--color-gold-border);font-size:12px;">专业门禁</span>'),
    ('<span style="font-size:24px;">⚖</span>', '<span class="badge" style="background:var(--color-gold-bg);color:var(--color-gold);border:1px solid var(--color-gold-border);font-size:12px;">专业门禁</span>'),
    ('<span>💡</span> 悟堂沟通导师观察与反馈', '悟堂沟通导师观察与反馈'),

    # Gallery & 108
    ('🖨️ A4 拼版打印预览 (一页9张)', 'A4 拼版打印预览 (一页9张)'),
    ('🖨 A4 拼版打印预览 (一页9张)', 'A4 拼版打印预览 (一页9张)'),
    ('随机参悟一鉴 ✨', '随机参悟一鉴'),
    ('🖨️ 调用系统打印机立即打印 (Ctrl+P)', '调用系统打印机立即打印 (Ctrl+P)'),
    ('🖨 调用系统打印机立即打印 (Ctrl+P)', '调用系统打印机立即打印 (Ctrl+P)'),
    ('随机抽取觉察牌 ✨', '随机抽取觉察牌'),

    # Privacy & Rules
    ('<span>🛡️</span>', '<span class="badge" style="background:#EBF3ED;color:#2B6E3F;font-size:12px;">安全规范</span>'),
    ('<span>🛡</span>', '<span class="badge" style="background:#EBF3ED;color:#2B6E3F;font-size:12px;">安全规范</span>'),
    ('📥 导出全量本地数据 (JSON)', '导出全量本地数据 (JSON)'),
    ('🗑️ 彻底清空本地所有记录', '彻底清空本地所有记录'),
    ('🗑 彻底清空本地所有记录', '彻底清空本地所有记录'),
    ('<div class="rule-icon">🔒</div>', '<div class="rule-icon" style="font-size:13px;font-weight:700;">一</div>'),
    ('<div class="rule-icon">🌿</div>', '<div class="rule-icon" style="font-size:13px;font-weight:700;">二</div>'),
    ('<div class="rule-icon">🏥</div>', '<div class="rule-icon" style="font-size:13px;font-weight:700;">三</div>'),
    ('<div class="rule-icon">📞</div>', '<div class="rule-icon" style="font-size:13px;font-weight:700;">四</div>'),
    ('<span style="font-size:20px;">👑</span>', '<span class="badge" style="background:#9F7430;color:#FFF;font-size:11px;">主理人</span>'),
    ('⚡ 一键填入默认主理人账号 (admin / admin)', '一键填入默认主理人账号 (admin / admin)'),
    ('⚠️ 两次输入的密码不一致，请仔细核对', '两次输入的密码不一致，请仔细核对'),
    ('⚠ 两次输入的密码不一致，请仔细核对', '两次输入的密码不一致，请仔细核对'),
    ('<div class="bgm-disc">♫</div>', '<div class="bgm-disc" style="font-size:13px;font-weight:600;">乐</div>'),

    # JS Code strings
    ("showToast('主理人身份已认证！顶栏已自动解锁「主理人工作台」👑');", "showToast('主理人身份已认证！顶栏已自动解锁「主理人工作台」');"),
    ("showToast('主理人身份已认证 (本地兼容态)！👑');", "showToast('主理人身份已认证 (本地兼容态)！');"),
    ("👑 主理人已认证", "主理人已认证"),
    ("btn.textContent = '🌿 悟堂 AI 正在倾听与梳理…';", "btn.textContent = '悟堂 AI 正在倾听与梳理…';"),
    ("btn.textContent = '🌿 AI 结构化梳理心绪';", "btn.textContent = 'AI 结构化梳理心绪';"),
    (" + (hasCheckin ? ' 🌿' : '') + ", " + (hasCheckin ? ' [已修]' : '') + "),
    ("📞 <a href=\"tel:", "服务热线：<a href=\"tel:"),
    ("'★ 已珍藏' : '☆ 珍藏此卡'", "'已珍藏' : '珍藏此卡'"),
    ("isFav ? '★' : '☆'", "isFav ? '已藏' : '收藏'"),
    ("'💡 觉察问句：'", "'觉察问句：'"),
    ("favBtnText.textContent = isFav ? '✓ 已收入珍藏' : '⭐ 收入珍藏';", "favBtnText.textContent = isFav ? '已收入珍藏' : '收入珍藏';"),
    ("favBtnText.textContent = isFav ? '✓ 已收入珍藏' : '收入珍藏';", "favBtnText.textContent = isFav ? '已收入珍藏' : '收入珍藏';"),
    ("if ($('btnCollectResonantCardText')) $('btnCollectResonantCardText').textContent = '✓ 已收入珍藏';", "if ($('btnCollectResonantCardText')) $('btnCollectResonantCardText').textContent = '已收入珍藏';"),
    ("<button class=\"btn sm secondary\" id=\"btnZen96FavToggle\" onclick=\"toggleZen96ModalFav()\">☆ 珍藏此卡</button>", "<button class=\"btn sm secondary\" id=\"btnZen96FavToggle\" onclick=\"toggleZen96ModalFav()\">珍藏此卡</button>"),
    ("floatingText.textContent = isPlaying ? ('♫ ' + curTrack.name) : '静心音乐: 关';", "floatingText.textContent = isPlaying ? ('禅音: ' + curTrack.name) : '静心音乐: 关';"),
    ("volIcon.textContent = volume === 0 ? '🔇' : (volume < 0.5 ? '🔉' : '🔊');", "volIcon.textContent = volume === 0 ? '静音' : '音量';"),
    ("(isActive && isPlaying ? '🔊' : (isActive ? '🎵' : '⚪'))", "(isActive && isPlaying ? '播放中' : (isActive ? '待播' : '○'))"),
    ("'<div style=\"font-size:32px;margin-bottom:8px;\">🍃</div>'", "'<div style=\"font-size:14px;color:var(--color-primary);font-weight:600;margin-bottom:8px;\">【禅意境】</div>'"),
]

count = 0
for old, new in replacements:
    if old in c:
        c = c.replace(old, new)
        count += 1
    else:
        # print missing to verify
        pass

print(f"Direct replacements applied: {count}/{len(replacements)}")

# General cleanup for remaining emoji pictographs in the range
# Emojis in range U+1F000 to U+1FAFF, plus common pictorial symbols
emoji_pattern = re.compile(r'[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u274B\u274D-\u27BF]')
# Filter out matches
remaining = emoji_pattern.findall(c)
print(f"Remaining emojis found: {len(remaining)} -> {set(remaining)}")

# Strip any residual emojis cleanly
c = emoji_pattern.sub('', c)

with open('frontend/_template.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Saved frontend/_template.html successfully.")
