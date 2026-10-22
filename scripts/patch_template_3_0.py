# -*- coding: utf-8 -*-
"""
悟堂 · 东方解忧处 —— PRD 3.0 模板增强补丁
负责将 PRD 3.0 的所有模块（CSS、导航、成长记录、心境健康、情境练习、卡牌典藏、数据与授权中心、JS 交互引擎）
注入 frontend/_template.html 并保证完全兼容。
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

def patch_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. 注入 PRD 3.0 专属 CSS (插在 </style> 之前)
    css_3_0 = """
/* ==========================================================================
   PRD 3.0 现代东方编辑设计扩展：成长记录、心境健康、情境练习室、卡牌典藏
   ========================================================================== */
.mode-nav {
  display: inline-flex;
  background: #EBE5DB;
  padding: 3px;
  border-radius: 30px;
  border: 1px solid #DFD8CC;
  overflow-x: auto;
  max-width: 100%;
  white-space: nowrap;
  -webkit-overflow-scrolling: touch;
}
.mode-nav::-webkit-scrollbar { display: none; }

/* 情绪标签选择组 (F-10) */
.mood-chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0;
}
.mood-chip {
  padding: 7px 14px;
  border-radius: 20px;
  background: var(--color-surface-subtle);
  border: 1px solid var(--color-border);
  font-size: 13.5px;
  color: var(--color-ink-light);
  cursor: pointer;
  transition: all var(--trans);
  user-select: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.mood-chip:hover {
  border-color: var(--color-primary-border);
  background: var(--color-primary-light);
}
.mood-chip.active {
  background: var(--color-primary);
  color: #FFF;
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(142,41,39,0.25);
}

/* 压力与精力滑块/药丸组 */
.level-pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0 16px;
}
.level-pill {
  flex: 1;
  min-width: 60px;
  text-align: center;
  padding: 7px 10px;
  font-size: 12.5px;
  border-radius: 8px;
  background: var(--color-surface-subtle);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--trans);
  color: var(--color-ink-light);
}
.level-pill.active {
  background: var(--color-gold-bg);
  border-color: var(--color-gold);
  color: var(--color-gold);
  font-weight: 600;
}

/* 日记与微行动卡片 */
.journal-item-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 14px;
  transition: all var(--trans);
}
.journal-item-card:hover {
  box-shadow: var(--shadow-sm);
  border-color: var(--color-border-dark);
}
.journal-dim-box {
  background: var(--color-surface-subtle);
  border-left: 3px solid var(--color-primary);
  padding: 10px 14px;
  border-radius: 0 8px 8px 0;
  margin: 8px 0;
  font-size: 13.5px;
  line-height: 1.6;
}

/* 情境练习室 */
.chat-window {
  background: #FAF8F5;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 18px;
  min-height: 220px;
  max-height: 380px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 14px;
}
.chat-msg {
  max-width: 82%;
  padding: 10px 15px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}
.chat-msg.role-ai {
  align-self: flex-start;
  background: #FFF;
  border: 1px solid var(--color-border);
  color: var(--color-ink);
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.chat-msg.role-user {
  align-self: flex-end;
  background: linear-gradient(135deg, #962E2D 0%, #7E201F 100%);
  color: #FFF;
}
.feedback-box {
  background: #FCF9F3;
  border: 1px solid #EADBCC;
  border-radius: 10px;
  padding: 16px 18px;
  margin-top: 14px;
}
.alt-quote-card {
  background: #FFF;
  border-left: 3px solid #3A6D4F;
  border: 1px solid var(--color-border);
  border-left-width: 3px;
  padding: 12px 14px;
  border-radius: 0 8px 8px 0;
  margin-bottom: 8px;
  font-size: 13.5px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

/* 自评量表卡片与题目 */
.assessment-question-item {
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border);
}
.assessment-question-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-ink);
  margin-bottom: 10px;
  line-height: 1.5;
}
.scale-options-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.scale-radio-btn {
  padding: 6px 13px;
  border-radius: 18px;
  border: 1px solid var(--color-border);
  background: #FFF;
  font-size: 12.5px;
  cursor: pointer;
  transition: all var(--trans);
  color: var(--color-ink-light);
}
.scale-radio-btn:hover {
  background: var(--color-surface-subtle);
  border-color: var(--color-primary-border);
}
.scale-radio-btn.selected {
  background: var(--color-primary);
  color: #FFF;
  border-color: var(--color-primary);
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(142,41,39,0.2);
}

/* 主题卡牌包网格 */
.theme-pack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin-top: 16px;
}
.theme-pack-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all var(--trans);
  position: relative;
}
.theme-pack-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-primary-border);
  box-shadow: var(--shadow-sm);
}
.theme-pack-card.active {
  border-color: var(--color-primary);
  background: #FDFBF8;
  box-shadow: 0 0 0 1px var(--color-primary);
}

/* 日历小网格 */
.mini-calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
  text-align: center;
  margin-top: 10px;
}
.mini-cal-day {
  padding: 8px 4px;
  background: var(--color-surface-subtle);
  border-radius: 6px;
  font-size: 12px;
  color: var(--color-muted);
  border: 1px solid transparent;
}
.mini-cal-day.has-checkin {
  background: var(--color-primary-light);
  color: var(--color-primary);
  font-weight: bold;
  border-color: var(--color-primary-border);
}
.mini-cal-day.today {
  border-color: var(--color-gold);
}

/* 资源卡片网格 */
.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 14px;
  margin-top: 14px;
}
.resource-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.resource-card:hover {
  border-color: var(--color-border-dark);
  box-shadow: var(--shadow-sm);
}

/* 独立隐私授权矩阵行 */
.consent-row-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid var(--color-border);
  gap: 16px;
}
.consent-toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  flex-shrink: 0;
}
.consent-toggle-switch input { opacity: 0; width: 0; height: 0; }
.consent-slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #D6CFBE;
  transition: .3s;
  border-radius: 24px;
}
.consent-slider:before {
  position: absolute;
  content: "";
  height: 18px; width: 18px;
  left: 3px; bottom: 3px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}
input:checked + .consent-slider { background-color: var(--color-primary); }
input:checked + .consent-slider:before { transform: translateX(20px); }
"""

    if "PRD 3.0 现代东方编辑设计扩展" not in html:
        html = html.replace("</style>", css_3_0 + "\n</style>")

    # 2. 更新顶栏核心导航 (6个核心入口 + 1个主理人入口)
    old_nav = """      <nav class="mode-nav" aria-label="核心导航">
        <button class="mode-tab active" id="tabRelief" title="东方解忧咨询与抽牌">解忧</button>
        <button class="mode-tab" id="tabMine" title="个人足迹、历史记录与隐私">我的</button>
        <button class="mode-tab hidden" id="tabStudio" title="主理人工作台（主理人专享）" style="display:none;">
          <span style="font-size:12px;margin-right:2px;">👑</span> 主理人工作台
        </button>
      </nav>"""

    new_nav = """      <nav class="mode-nav" aria-label="核心导航">
        <button class="mode-tab active" id="tabRelief" title="东方解忧咨询与抽牌">解忧</button>
        <button class="mode-tab" id="tabGrowth" title="每日心境、AI心事日记与微行动复盘">成长记录</button>
        <button class="mode-tab" id="tabWellbeing" title="心境健康自评与专业资源导航">心境健康</button>
        <button class="mode-tab" id="tabPractice" title="情境练习室与沟通助手">情境练习</button>
        <button class="mode-tab" id="tabCards" title="卡牌典藏与主题卡牌包">卡牌典藏</button>
        <button class="mode-tab" id="tabMine" title="个人足迹、数据管理与授权">我的</button>
        <button class="mode-tab hidden" id="tabStudio" title="主理人工作台（主理人专享）" style="display:none;">
          <span style="font-size:12px;margin-right:2px;">👑</span> 主理人
        </button>
      </nav>"""

    if old_nav in html:
        html = html.replace(old_nav, new_nav)

    # 3. 注入 PRD 3.0 的新主区域: growthArea, wellbeingArea, practiceArea, cardsArea
    # 插在 </main>\n\n\n  <!-- 第二部分：用户端「我的」 之前
    growth_html = """
  <!-- ======================================================================
       第三部分：用户端「成长记录」（每日心境签到、AI 心事日记、微行动复盘、日历周回顾、成长地图）
       ====================================================================== -->
  <main id="growthArea" class="hidden">
    <div style="display:flex;flex-direction:column;gap:18px;">

      <!-- 模块 1: 每日心境签到 (F-10 / 18.2) -->
      <section class="card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
          <div>
            <span class="badge ok" style="margin-bottom:6px;">日常觉察 · 每日签到</span>
            <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">今天的你，感觉怎么样？</h2>
            <p style="margin:0;font-size:13.5px;color:var(--color-muted);">
              用 10-30 秒留下今天的主观心绪。支持跳过，不作疾病判断，仅保存在本地设备。
            </p>
          </div>
          <div style="font-size:12px;color:var(--color-gold);background:var(--color-gold-bg);border:1px solid var(--color-gold-border);padding:4px 10px;border-radius:14px;" id="checkinTodayDateBadge">
            今日：2026-10-19
          </div>
        </div>

        <div style="margin-top:16px;">
          <div class="section-label" style="font-size:13px;margin-bottom:6px;">选择符合当下的感受标签（可多选）：</div>
          <div class="mood-chip-group" id="moodChipGroup">
            <div class="mood-chip" data-mood="calm"><span>🌿</span> 平静从容</div>
            <div class="mood-chip" data-mood="joy"><span>✨</span> 充实欣喜</div>
            <div class="mood-chip" data-mood="tired"><span>🍂</span> 疲惫有些透支</div>
            <div class="mood-chip" data-mood="anxious"><span>🌪️</span> 焦虑心慌</div>
            <div class="mood-chip" data-mood="frustrated"><span>🔥</span> 烦躁窝火</div>
            <div class="mood-chip" data-mood="sad"><span>🌧️</span> 沮丧失落</div>
            <div class="mood-chip" data-mood="overthinking"><span>🌀</span> 内耗反刍</div>
            <div class="mood-chip" data-mood="relieved"><span>☁️</span> 释怀看开</div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:14px;margin-top:14px;">
          <div>
            <div class="section-label" style="font-size:13px;margin-bottom:6px;">当前的精力状态：</div>
            <div class="level-pill-group" id="energyPillGroup">
              <div class="level-pill" data-level="high">充沛 ⚡</div>
              <div class="level-pill active" data-level="normal">一般 🔋</div>
              <div class="level-pill" data-level="low">疲惫 🪫</div>
              <div class="level-pill" data-level="drained">透支 💤</div>
            </div>
          </div>
          <div>
            <div class="section-label" style="font-size:13px;margin-bottom:6px;">主观压力感受：</div>
            <div class="level-pill-group" id="stressPillGroup">
              <div class="level-pill" data-level="very_low">很轻</div>
              <div class="level-pill active" data-level="low">较轻</div>
              <div class="level-pill" data-level="moderate">一般</div>
              <div class="level-pill" data-level="high">较大</div>
              <div class="level-pill" data-level="very_high">很大</div>
            </div>
          </div>
        </div>

        <div style="margin-top:6px;">
          <input type="text" id="checkinNoteInput" class="form-input" placeholder="留下一句属于今天的心语（选填，如：今天按时关掉了电脑）" style="width:100%;box-sizing:border-box;font-size:13.5px;padding:9px 14px;">
        </div>

        <div style="margin-top:16px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
          <button class="btn" id="btnSubmitCheckin">留下今日心境印记</button>
          <span style="font-size:12px;color:var(--color-muted);">* 悟堂遵循最小权限：未点保存不上传、不推断。</span>
        </div>

        <!-- 签到成功温馨反馈 -->
        <div id="checkinFeedbackBox" class="hidden" style="margin-top:18px;background:var(--color-primary-light);border:1px solid var(--color-primary-border);border-radius:10px;padding:16px;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span style="font-size:20px;">🍵</span>
            <strong style="color:var(--color-primary);font-size:15px;" id="checkinFeedbackTitle">已安顿好今日心境</strong>
          </div>
          <p style="margin:0 0 10px;font-size:13.5px;color:var(--color-ink-light);" id="checkinFeedbackDesc">
            听见了你今天的感受。不管经历了什么，这一刻能停下来观照自己，就是了不起的修行。
          </p>
          <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <button class="btn sm" id="btnCheckinGoCard">查看今日推荐觉察卡 →</button>
            <button class="btn sm secondary" id="btnCheckinReset">重新签到</button>
          </div>
        </div>
      </section>

      <!-- 模块 2: AI 心事日记 (F-12 / 18.3) -->
      <section class="card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
          <div>
            <span class="badge rev" style="margin-bottom:6px;">情绪外化 · 结构化整理</span>
            <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">AI 心事日记 · 把乱麻理出头绪</h2>
            <p style="margin:0;font-size:13.5px;color:var(--color-muted);">
              写下让你放不下的碎碎念，AI 助手将帮你整理为客观事实、当时想法、情绪体验、内在需要与下一步。
            </p>
          </div>
        </div>

        <div style="margin-top:16px;">
          <textarea id="journalInputText" class="form-textarea" placeholder="写下今天的一件心事，或者想到什么写什么……（例如：今天和同事对方案，他当场否定了我，我特别难堪，总觉得别人都在看我笑话）" style="width:100%;box-sizing:border-box;min-height:90px;font-size:14px;padding:12px;line-height:1.6;"></textarea>
        </div>

        <div style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap;">
          <button class="btn" id="btnAiOrganizeJournal">🌿 AI 结构化梳理心绪</button>
          <button class="btn ghost sm" id="btnFillJournalSample">填入示范倾诉</button>
          <button class="btn secondary sm" id="btnClearJournalInput">清空</button>
        </div>

        <!-- 结构化整理结果呈现 -->
        <div id="journalStructuredResult" class="hidden" style="margin-top:20px;border-top:1px dashed var(--color-border);padding-top:16px;">
          <h3 style="font-family:var(--font-serif);font-size:17px;margin:0 0 10px;color:var(--color-ink);">AI 整理结果（所有推断已标明，可自由纠偏）：</h3>
          
          <div class="journal-dim-box">
            <strong style="color:var(--color-primary);">01 发生了什么（客观事实）：</strong>
            <p id="jResEvent" style="margin:3px 0 0;color:var(--color-ink-light);"></p>
          </div>
          
          <div class="journal-dim-box" style="border-left-color:var(--color-gold);">
            <strong style="color:var(--color-gold);">02 当时的想法（脑海评判）：</strong>
            <p id="jResThoughts" style="margin:3px 0 0;color:var(--color-ink-light);"></p>
          </div>

          <div class="journal-dim-box" style="border-left-color:#3A6D4F;">
            <strong style="color:#3A6D4F;">03 感受到的情绪：</strong>
            <div id="jResFeelings" style="display:flex;gap:6px;flex-wrap:wrap;margin-top:4px;"></div>
          </div>

          <div class="journal-dim-box" style="border-left-color:#8F2928;background:#FCF5F5;">
            <strong style="color:#8F2928;">04 可能在意的需要（【待你确认】）：</strong>
            <p id="jResNeeds" style="margin:3px 0 0;color:var(--color-ink);font-weight:500;"></p>
          </div>

          <div class="journal-dim-box" style="border-left-color:#2E7D32;">
            <strong style="color:#2E7D32;">05 愿意尝试的下一步（微行动）：</strong>
            <p id="jResNextStep" style="margin:3px 0 0;color:var(--color-ink-light);"></p>
          </div>

          <div style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap;">
            <button class="btn" id="btnSaveJournalToLocal">保存至我的日记本</button>
            <button class="btn secondary" id="btnDiscardJournal">丢弃不保存</button>
          </div>
        </div>
      </section>

      <!-- 模块 3: 今日微行动与行动复盘 (F-11 / 18.7) -->
      <section class="card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
          <div>
            <span class="badge rev" style="margin-bottom:6px;">行动闭环 · 非评判复盘</span>
            <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">今日微行动与行动复盘</h2>
            <p style="margin:0;font-size:13.5px;color:var(--color-muted);">
              行动永远是可自主选择的。不完成绝不代表意志力不足，系统绝不使用指责语言。
            </p>
          </div>
        </div>

        <div style="margin-top:14px;background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:10px;padding:16px;">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:18px;">🌱</span>
            <strong style="font-size:15px;color:var(--color-ink);" id="currentMicroActionTitle">今晚 5 分钟：把「事实」与「评价」分栏写下</strong>
          </div>
          <p style="margin:0;font-size:13px;color:var(--color-muted);" id="currentMicroActionDesc">
            拿出一张纸划一道竖线，左边写事情经过，右边写脑海评判，写完合上即可。
          </p>
        </div>

        <div style="margin-top:14px;">
          <div class="section-label" style="font-size:13px;margin-bottom:8px;">点击反馈你的微行动执行状态：</div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(130px, 1fr));gap:8px;" id="actionFeedbackBtnGroup">
            <button class="btn sm secondary" data-action-status="completed">已做到了 🌿</button>
            <button class="btn sm secondary" data-action-status="partial">做了一部分 ✨</button>
            <button class="btn sm secondary" data-action-status="not_started">还没开始 ⏳</button>
            <button class="btn sm secondary" data-action-status="unsuitable">方法不适合我 🔄</button>
          </div>
          <div id="actionFeedbackToast" class="hidden" style="margin-top:10px;font-size:13px;padding:8px 12px;border-radius:6px;background:var(--color-primary-light);color:var(--color-primary);"></div>
        </div>
      </section>

      <!-- 模块 4: 心境日历与每周回顾 (F-13 / 18.4) -->
      <section class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
          <div>
            <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">心境日历与成长线索</h2>
            <p style="margin:0;font-size:13px;color:var(--color-muted);">真实记录你的每一次驻足与自我觉察</p>
          </div>
          <div style="font-size:12px;color:var(--color-muted);" id="calMonthLabel">2026 年 10 月</div>
        </div>

        <div class="mini-calendar-grid" id="miniCalendarGrid"></div>

        <div style="margin-top:18px;background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:10px;padding:16px;">
          <h3 style="font-family:var(--font-serif);font-size:16px;margin:0 0 6px;display:flex;align-items:center;gap:6px;">
            <span>📜</span> 本周觉察回顾摘要
          </h3>
          <p style="margin:0;font-size:13.5px;color:var(--color-ink-light);line-height:1.65;" id="weeklyReviewSummary">
            本周已沉淀 1 条心境签到。根据 PRD 3.0 规范：记录尚少时不擅自推断情绪周期与疾病趋势，先为你静静守护每一天的心声。
          </p>
        </div>
      </section>

      <!-- 模块 5: 情绪触发地图与个人成长目标 (F-14 / 18.5 / 18.6) -->
      <section class="card">
        <h2 style="font-family:var(--font-serif);margin:0 0 6px;font-size:22px;">情绪触发地图 · 个人成长地图</h2>
        <p style="margin:0 0 16px;font-size:13.5px;color:var(--color-muted);">
          识别你的敏感场景与习惯应对，自定成长节奏，无惩罚式打卡。
        </p>

        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:14px;">
          <div style="background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:10px;padding:16px;">
            <h4 style="margin:0 0 8px;font-size:15px;color:var(--color-primary);font-family:var(--font-serif);">🧭 情绪触发场景归纳</h4>
            <ul style="margin:0;padding-left:18px;font-size:13px;color:var(--color-ink-light);line-height:1.7;" id="triggerMapList">
              <li>临时加塞的任务 ➔ 容易触发急躁与被越界感</li>
              <li>公众发言被挑错 ➔ 容易触发自我怀疑与内耗反刍</li>
            </ul>
          </div>
          <div style="background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:10px;padding:16px;">
            <h4 style="margin:0 0 8px;font-size:15px;color:var(--color-gold);font-family:var(--font-serif);">🌱 当前成长主题：关系边界</h4>
            <p style="margin:0 0 10px;font-size:13px;color:var(--color-ink-light);">
              目标：在面对非必须的帮忙请求时，练习先停顿 3 秒再答复。
            </p>
            <span class="badge ok" style="font-size:11px;">自定节奏 · 随时可暂停</span>
          </div>
        </div>
      </section>

    </div>
  </main>


  <!-- ======================================================================
       第四部分：用户端「心境健康中心」（标准化自评、量表门禁、专业资源导航、授权转介）
       ====================================================================== -->
  <main id="wellbeingArea" class="hidden">
    <div style="display:flex;flex-direction:column;gap:18px;">

      <!-- 顶部门禁与免责警示 -->
      <section class="card" style="border-left:4px solid var(--color-gold);">
        <div style="display:flex;align-items:flex-start;gap:12px;">
          <span style="font-size:24px;">⚖️</span>
          <div>
            <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:20px;">悟堂心境健康中心 · 专业审核门禁</h2>
            <p style="margin:0;font-size:13.5px;color:var(--color-ink-light);line-height:1.65;">
              本中心提供经专业伦理与临床心理顾问核验的标准化心理自评工具及权威就医导航。
              <strong>自评结果仅供自我觉察与就诊沟通参考，不属于精神科临床诊断或医疗处方。</strong>
              计分均由确定性程序计算，严禁大模型擅自估算分数。
            </p>
          </div>
        </div>
      </section>

      <!-- 量表展示卡片：PSS-10 (活跃) + GAD-7/PHQ-9 (禁用/预览态) -->
      <section class="card">
        <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">标准化心理自评量表</h2>
        <p style="margin:0 0 16px;font-size:13.5px;color:var(--color-muted);">请选择获准开放的量表进行自我了解</p>

        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:14px;">
          <!-- 1. PSS-10 -->
          <div style="background:var(--color-surface);border:1.5px solid var(--color-primary);border-radius:12px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span class="badge ok">已核准 · 可作答</span>
                <span style="font-size:11px;color:var(--color-muted);">10 题 · 约3分钟</span>
              </div>
              <h3 style="font-family:var(--font-serif);margin:0 0 6px;font-size:18px;color:var(--color-ink);">知觉心理压力量表 (PSS-10)</h3>
              <p style="margin:0;font-size:12.5px;color:var(--color-ink-light);line-height:1.6;">
                评估过去一个月内，您在生活与工作中感受到的不可控、超负荷与主观压力程度。
              </p>
            </div>
            <button class="btn sm" id="btnOpenPss10" style="margin-top:16px;">开始知觉压力自评 →</button>
          </div>

          <!-- 2. GAD-7 (禁用态) -->
          <div style="background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:12px;padding:18px;opacity:0.85;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span class="badge rev">专家审核中 · 暂缓开放</span>
                <span style="font-size:11px;color:var(--color-muted);">PRD 4.4 门禁</span>
              </div>
              <h3 style="font-family:var(--font-serif);margin:0 0 6px;font-size:18px;color:#6B645B;">广泛性焦虑量表 (GAD-7)</h3>
              <p style="margin:0;font-size:12.5px;color:var(--color-muted);line-height:1.6;">
                临床症状筛查量表。坚守 PRD 3.0 门禁铁律：需完成本地医疗伦理终审后开放，禁止伪造测试分数。
              </p>
            </div>
            <button class="btn sm secondary" disabled style="margin-top:16px;">待专家审核上线</button>
          </div>

          <!-- 3. PHQ-9 (禁用态) -->
          <div style="background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:12px;padding:18px;opacity:0.85;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span class="badge rev">专家审核中 · 暂缓开放</span>
                <span style="font-size:11px;color:var(--color-muted);">PRD 4.4 门禁</span>
              </div>
              <h3 style="font-family:var(--font-serif);margin:0 0 6px;font-size:18px;color:#6B645B;">抑郁症状问卷 (PHQ-9)</h3>
              <p style="margin:0;font-size:12.5px;color:var(--color-muted);line-height:1.6;">
                涉及高敏感自伤题目，必须建立专科转介安全闭环。当前保持禁用状态。
              </p>
            </div>
            <button class="btn sm secondary" disabled style="margin-top:16px;">待专家审核上线</button>
          </div>
        </div>

        <!-- PSS-10 作答互动区 (默认隐藏，点击展开) -->
        <div id="pss10QuizContainer" class="hidden" style="margin-top:24px;border-top:1px dashed var(--color-border);padding-top:20px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
            <h3 style="font-family:var(--font-serif);font-size:19px;margin:0;">知觉心理压力量表 (PSS-10) 测评题目</h3>
            <button class="btn sm ghost" id="btnClosePss10">收起题目</button>
          </div>
          <p style="font-size:13px;color:var(--color-muted);margin:0 0 16px;">
            请回顾【过去一个月】的实际生活体验，根据最贴近的真实发生频率作答：
          </p>

          <div id="pss10QuestionsList"></div>

          <div style="margin-top:20px;display:flex;gap:12px;align-items:center;">
            <button class="btn lg" id="btnSubmitPss10">交卷并生成自评报告</button>
            <span style="font-size:12px;color:var(--color-muted);">由确定性规则实时计分</span>
          </div>
        </div>

        <!-- PSS-10 结果报告单呈现 -->
        <div id="pss10ResultCard" class="hidden" style="margin-top:24px;background:#FCF9F3;border:1.5px solid #DFCDB7;border-radius:12px;padding:24px;">
          <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #E8DCBF;padding-bottom:12px;margin-bottom:16px;">
            <div>
              <span class="badge ok" id="pss10LevelBadge">中度压力区间</span>
              <h3 style="font-family:var(--font-serif);margin:6px 0 0;font-size:22px;color:var(--color-primary);">知觉心理压力自评报告</h3>
            </div>
            <div style="text-align:right;">
              <div style="font-size:32px;font-weight:700;color:var(--color-primary);line-height:1;" id="pss10ScoreVal">21</div>
              <div style="font-size:11px;color:var(--color-muted);margin-top:2px;">满分 40 分</div>
            </div>
          </div>

          <!-- 高危安全求助提示（若触发） -->
          <div id="pss10SafetyAlert" class="hidden" style="background:#FDF2F2;border:1px solid #ECC4C4;border-radius:8px;padding:12px 14px;margin-bottom:16px;color:#9B3131;font-size:13px;line-height:1.6;">
            <strong>安全关怀提示：</strong> <span id="pss10SafetyText"></span>
          </div>

          <div style="font-size:14px;color:var(--color-ink-light);line-height:1.75;margin-bottom:14px;" id="pss10SummaryText"></div>

          <div class="journal-dim-box" style="border-left-color:var(--color-gold);background:#FAF6EE;">
            <strong style="color:var(--color-gold);">东方先贤解法视界：</strong>
            <p id="pss10WisdomText" style="margin:4px 0 0;color:var(--color-ink);"></p>
          </div>

          <div style="margin-top:14px;">
            <strong style="font-size:13.5px;color:var(--color-ink);">推荐的温和调适建议：</strong>
            <ul id="pss10NextStepsList" style="margin:6px 0 0;padding-left:20px;font-size:13px;color:var(--color-ink-light);line-height:1.7;"></ul>
          </div>

          <div style="margin-top:20px;border-top:1px dashed #DFCDB7;padding-top:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div style="font-size:12px;color:var(--color-muted);">* 自评不等于医学诊断。若感身心过载，建议向下方专业机构求助。</div>
            <div style="display:flex;gap:8px;">
              <button class="btn sm" id="btnSavePss10History">保存自评记录</button>
              <button class="btn sm secondary" id="btnRetakePss10">重新测验</button>
            </div>
          </div>
        </div>
      </section>

      <!-- 模块 2: 专业资源导航 (F-17 / 18.11) -->
      <section class="card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
          <div>
            <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">经核验的专业心理健康与危机资源导航</h2>
            <p style="margin:0;font-size:13px;color:var(--color-muted);">
              严谨核验地区、服务类型、官方联系方式及最后核验日期（2026-10-19）。
            </p>
          </div>
          <div style="display:flex;gap:8px;">
            <select class="form-select" id="resourceRegionFilter" style="width:auto;padding:6px 12px;font-size:13px;">
              <option value="全部">全部地区</option>
              <option value="全国">全国热线</option>
              <option value="北京">北京</option>
              <option value="上海">上海</option>
              <option value="广东">广东</option>
              <option value="浙江">浙江</option>
            </select>
          </div>
        </div>

        <div class="resource-grid" id="resourceListGrid"></div>
      </section>

      <!-- 模块 3: 授权转介沟通摘要 (F-17 / 18.11) -->
      <section class="card">
        <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">生成面询沟通清单（授权转介摘要）</h2>
        <p style="margin:0 0 16px;font-size:13.5px;color:var(--color-muted);">
          前往专科医院心理门诊或预约心理咨询师前，将主诉与自评梳理成条理清晰的沟通清单，避免因紧张而遗漏重点。
        </p>

        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));gap:12px;">
          <div>
            <label style="display:block;font-size:12.5px;color:var(--color-ink-light);margin-bottom:4px;">主要困扰概括：</label>
            <input type="text" id="referralComplaintInput" class="form-input" placeholder="如：工作过度消耗、入睡困难与情绪反刍" style="width:100%;box-sizing:border-box;font-size:13.5px;padding:8px 12px;">
          </div>
          <div>
            <label style="display:block;font-size:12.5px;color:var(--color-ink-light);margin-bottom:4px;">困扰持续时间：</label>
            <input type="text" id="referralDurationInput" class="form-input" placeholder="如：近 3 周 / 2 个月" style="width:100%;box-sizing:border-box;font-size:13.5px;padding:8px 12px;">
          </div>
        </div>

        <div style="margin-top:14px;">
          <button class="btn" id="btnGenerateReferral">一键生成就医/面询沟通清单</button>
        </div>

        <div id="referralSummaryBox" class="hidden" style="margin-top:16px;background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:10px;padding:16px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <h4 style="margin:0;font-family:var(--font-serif);font-size:16px;" id="refSumTitle">日常压力沟通清单</h4>
            <button class="btn sm secondary" id="btnCopyReferralSummary">复制清单文本</button>
          </div>
          <div id="refSumBody" style="font-size:13.5px;line-height:1.7;color:var(--color-ink-light);"></div>
        </div>
      </section>

    </div>
  </main>


  <!-- ======================================================================
       第五部分：用户端「情境练习室」（5 大场景沟通演练、AI 角色扮演与替代表达反馈）
       ====================================================================== -->
  <main id="practiceArea" class="hidden">
    <div style="display:flex;flex-direction:column;gap:18px;">

      <section class="card">
        <span class="badge ok" style="margin-bottom:6px;">情境演练 · 替代表达</span>
        <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">情境练习室 · 沟通助手</h2>
        <p style="margin:0;font-size:13.5px;color:var(--color-muted);">
          在安全的环境中，练习职场与人际边界沟通。AI 扮演对话对象，提供 4 维非评判反馈与高情商替代表达。
        </p>

        <!-- 场景切换卡片网格 -->
        <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(240px, 1fr));gap:12px;margin-top:18px;" id="practiceScenarioCardsGrid"></div>
      </section>

      <!-- 交互演练对话室卡片 -->
      <section class="card" id="practiceActiveRoom" style="border:1.5px solid var(--color-border-dark);">
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--color-border);padding-bottom:12px;margin-bottom:14px;flex-wrap:wrap;gap:8px;">
          <div>
            <h3 style="font-family:var(--font-serif);margin:0 0 2px;font-size:18px;" id="practiceRoomTitle">拒绝不合理请求</h3>
            <div style="font-size:12.5px;color:var(--color-muted);" id="practiceRoomRoleDesc">扮演对象：同事小陈</div>
          </div>
          <button class="btn sm secondary" id="btnResetPracticeScenario">重新开始本场景</button>
        </div>

        <!-- 模拟对话气泡窗口 -->
        <div class="chat-window" id="practiceChatWindow"></div>

        <!-- 用户练习输入框 -->
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <input type="text" id="practiceDraftInput" class="form-input" placeholder="输入你想好的一句话，点击发送练习（例如：抱歉啊小陈，我手头时间排满了）" style="flex:1;min-width:200px;font-size:14px;padding:10px 14px;">
          <button class="btn" id="btnSendPracticeMessage">发送练习</button>
        </div>

        <!-- 沟通反馈与替代表达呈现 -->
        <div id="practiceFeedbackBox" class="hidden feedback-box">
          <h4 style="margin:0 0 10px;font-family:var(--font-serif);font-size:16px;color:var(--color-primary);display:flex;align-items:center;gap:6px;">
            <span>💡</span> 悟堂沟通导师观察与反馈
          </h4>

          <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:10px;margin-bottom:12px;">
            <div style="background:#FFF;padding:10px 12px;border-radius:8px;border:1px solid #E8DFCE;">
              <strong style="font-size:12.5px;color:#8F2928;">边界清晰度：</strong>
              <div id="pfBoundaryText" style="font-size:13px;color:var(--color-ink-light);margin-top:2px;"></div>
            </div>
            <div style="background:#FFF;padding:10px 12px;border-radius:8px;border:1px solid #E8DFCE;">
              <strong style="font-size:12.5px;color:#9F7430;">语气与体面：</strong>
              <div id="pfToneText" style="font-size:13px;color:var(--color-ink-light);margin-top:2px;"></div>
            </div>
          </div>

          <div style="background:#FFF;padding:10px 12px;border-radius:8px;border:1px solid #E8DFCE;margin-bottom:12px;">
            <strong style="font-size:12.5px;color:#3A6D4F;">微调建议：</strong>
            <div id="pfAdviceText" style="font-size:13px;color:var(--color-ink-light);margin-top:2px;"></div>
          </div>

          <h5 style="margin:12px 0 6px;font-size:13.5px;color:var(--color-ink);">推荐的替代表达范式（点击复制）：</h5>
          <div id="pfAlternativesContainer"></div>
        </div>
      </section>

    </div>
  </main>


  <!-- ======================================================================
       第六部分：用户端「卡牌典藏」（6 大主题卡牌包、我的卡牌收藏与禅意图鉴）
       ====================================================================== -->
  <main id="cardsArea" class="hidden">
    <div style="display:flex;flex-direction:column;gap:18px;">

      <!-- 6 大主题卡牌包 (PRD 3.0 Section 18.12) -->
      <section class="card">
        <span class="badge ok" style="margin-bottom:6px;">主题牌组 · 先贤智慧</span>
        <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">东方解忧卡 · 主题卡牌包</h2>
        <p style="margin:0;font-size:13.5px;color:var(--color-muted);">
          按日常高频心境主题分类精选，点击浏览每个主题包的启发卡牌。
        </p>

        <div class="theme-pack-grid" id="themePackGridContainer"></div>
      </section>

      <!-- 主题包内卡牌详情展示区 -->
      <section class="card" id="themePackDetailSection">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
          <div>
            <h3 style="font-family:var(--font-serif);margin:0 0 4px;font-size:20px;" id="themePackDetailTitle">停止内耗 · 卡牌包</h3>
            <p style="margin:0;font-size:13px;color:var(--color-muted);" id="themePackDetailDesc"></p>
          </div>
        </div>

        <div class="studio-card-grid" id="themePackCardsList"></div>
      </section>

      <!-- 我的收藏夹 (Favorite Cards) -->
      <section class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">
          <div>
            <h3 style="font-family:var(--font-serif);margin:0 0 4px;font-size:20px;">我的珍藏卡牌</h3>
            <p style="margin:0;font-size:13px;color:var(--color-muted);" id="favCardsCountNotice">在此回看你在解忧旅途中收藏的心境、智慧与行动牌</p>
          </div>
        </div>
        <div class="studio-card-grid" id="favCardsContainer"></div>
      </section>

    </div>
  </main>
"""

    split_target = '<main id="mineArea" class="hidden">'
    if split_target in html and "growthArea" not in html:
        html = html.replace(split_target, growth_html + "\n\n  " + split_target)

    # 4. 在 mineArea 中注入【独立四级隐私授权矩阵】与【本地数据导出与清空】
    consent_panel_html = """
      <!-- PRD 3.0: 独立四级隐私授权管理中心 (F-19 / 10.2 / 10.6) -->
      <section class="card">
        <h3 style="font-family:var(--font-serif);font-size:18px;margin:0 0 6px;display:flex;align-items:center;gap:8px;">
          <span>🛡️</span>
          <span>独立隐私授权管理中心 (PRD 3.0 规范)</span>
        </h3>
        <p style="margin:0 0 16px;font-size:13px;color:var(--color-muted);">
          悟堂严守安全底线：AI 处理、本地记录、自评记录与公开案例使用完全物理隔离，未经单独授权绝不互通。
        </p>

        <div style="background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:10px;padding:0 18px;">
          <div class="consent-row-item">
            <div>
              <div style="font-weight:600;font-size:14px;color:var(--color-ink);">1. AI 瞬时解忧与对话处理</div>
              <div style="font-size:12.5px;color:var(--color-muted);">用于生成当次四步解忧方、AI日记整理或情境练习回复，瞬态流式处理后不留存敏感文本。</div>
            </div>
            <label class="consent-toggle-switch">
              <input type="checkbox" id="consentToggleAi" checked disabled>
              <span class="consent-slider"></span>
            </label>
          </div>

          <div class="consent-row-item">
            <div>
              <div style="font-weight:600;font-size:14px;color:var(--color-ink);">2. 本地成长记录保存（签到、日记、微行动）</div>
              <div style="font-size:12.5px;color:var(--color-muted);">允许将每日心境、心事日记与行动复盘保存在当前浏览器的 LocalStorage 中供随时回看。</div>
            </div>
            <label class="consent-toggle-switch">
              <input type="checkbox" id="consentToggleGrowth" checked>
              <span class="consent-slider"></span>
            </label>
          </div>

          <div class="consent-row-item">
            <div>
              <div style="font-weight:600;font-size:14px;color:var(--color-ink);">3. 心境健康标准化自评数据记录</div>
              <div style="font-size:12.5px;color:var(--color-muted);">允许在本地保存 PSS-10 压力自评分数与报告单，便于长期对比自身负荷变化。</div>
            </div>
            <label class="consent-toggle-switch">
              <input type="checkbox" id="consentToggleWellbeing" checked>
              <span class="consent-slider"></span>
            </label>
          </div>

          <div class="consent-row-item" style="border-bottom:none;">
            <div>
              <div style="font-weight:600;font-size:14px;color:var(--color-primary);">4. 公开内容共读与文章案例授权（严格独立）</div>
              <div style="font-size:12.5px;color:var(--color-muted);">默认关闭。仅在您明确勾选并经主理人人工脱敏后，方可作为公众号公益启发案例。</div>
            </div>
            <label class="consent-toggle-switch">
              <input type="checkbox" id="consentTogglePublic">
              <span class="consent-slider"></span>
            </label>
          </div>
        </div>

        <!-- 本地个人数据管理 (导出与彻底清空) -->
        <div style="margin-top:16px;padding-top:16px;border-top:1px dashed var(--color-border);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
          <div style="font-size:12.5px;color:var(--color-muted);">
            当前设备已存储：<span id="dataSummaryNotice" style="font-weight:600;color:var(--color-ink);">0 条足迹 · 0 次签到</span>
          </div>
          <div style="display:flex;gap:8px;">
            <button class="btn sm secondary" id="btnExportAllUserData">📥 导出全量本地数据 (JSON)</button>
            <button class="btn sm ghost" id="btnClearAllUserData" style="color:var(--color-danger);border-color:#F0C4C4;">🗑️ 彻底清空本地所有记录</button>
          </div>
        </div>
      </section>
"""

    privacy_module_target = '<!-- 模块 3: 隐私声明与边界保障 -->'
    if privacy_module_target in html and "独立隐私授权管理中心" not in html:
        html = html.replace(privacy_module_target, consent_panel_html + "\n\n      " + privacy_module_target)

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[ok] PRD 3.0 HTML & CSS sections injected into _template.html ({len(html):,} bytes)")

if __name__ == "__main__":
    patch_template()
