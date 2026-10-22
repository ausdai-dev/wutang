# -*- coding: utf-8 -*-
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = os.path.join("frontend", "_template.html")

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# ---------------------------------------------------------------------------
# 1. 注入 CSS 样式（在 </style> 之前）
# ---------------------------------------------------------------------------
CSS_INJECTION = """
/* ==========================================================================
   PRD 4.0 儒释道三学赛道、专属解脱之道 3D 卡牌与卡牌人生样式
   ========================================================================== */
.school-track-selector {
  margin: 14px 0 18px;
  padding: 14px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(34,31,27,0.02);
  transition: all 0.3s ease;
}
.school-track-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}
.school-track-title {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--color-ink);
  display: flex;
  align-items: center;
  gap: 6px;
}
.school-track-title::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 14px;
  background: var(--color-primary);
  border-radius: 2px;
}
.school-motto-badge {
  font-size: 12px;
  font-family: var(--font-serif);
  color: var(--color-gold);
  background: var(--color-gold-bg);
  padding: 3px 9px;
  border-radius: 12px;
  border: 1px solid var(--color-gold-border);
}
.school-track-pills {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 10px;
}
.school-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  background: var(--color-surface-subtle);
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  color: inherit;
}
.school-pill:hover {
  border-color: var(--color-primary-border);
  background: #FFF;
  transform: translateY(-1px);
}
.school-pill.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  box-shadow: 0 4px 14px rgba(142, 41, 39, 0.08);
}
.pill-seal {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-serif);
  font-weight: 700;
  font-size: 16px;
  color: var(--color-primary);
  flex-shrink: 0;
  transition: all 0.2s;
}
.school-pill.active .pill-seal {
  background: var(--color-primary);
  color: #FFF;
  border-color: var(--color-primary);
}
.pill-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.pill-name {
  font-size: 13.5px;
  font-weight: 700;
  color: var(--color-ink);
  line-height: 1.3;
}
.pill-desc {
  font-size: 11px;
  color: var(--color-muted);
  line-height: 1.3;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nickname-bar {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: var(--color-muted);
}
.nickname-input {
  padding: 5px 10px;
  font-size: 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: #FFF;
  width: 130px;
  color: var(--color-ink);
  font-family: inherit;
}
.nickname-input:focus {
  border-color: var(--color-primary);
  outline: none;
}

/* 专属解脱之道卡牌 3D 舞台 */
.liberation-hero-card {
  margin: 24px 0 28px;
  perspective: 1200px;
}
.liberation-card-3d {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
  aspect-ratio: 2.5 / 3.5;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  cursor: pointer;
  box-shadow: 0 16px 36px rgba(34,31,27,0.1), 0 2px 8px rgba(34,31,27,0.04);
  border-radius: 18px;
}
.liberation-card-3d.is-flipped {
  transform: rotateY(180deg);
}
.liberation-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border-radius: 18px;
  padding: 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border: 2px solid var(--color-border);
  background-size: cover;
  background-position: center;
}
.liberation-front {
  background: #FDFBF7;
  background-image: radial-gradient(circle at 50% 20%, rgba(255,255,255,0.9), rgba(246,242,233,0.96));
  border-color: var(--color-gold-border);
}
.liberation-back {
  background: #FAF8F2;
  transform: rotateY(180deg);
  border-color: var(--color-primary-border);
}
.card-inner-frame {
  position: absolute;
  inset: 10px;
  border: 1px solid var(--color-gold-border);
  border-radius: 12px;
  pointer-events: none;
}
.card-top-id {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-muted);
  letter-spacing: 0.5px;
  position: relative;
  z-index: 1;
}
.card-main-title {
  font-family: var(--font-serif);
  font-size: 44px;
  font-weight: 800;
  color: var(--color-primary);
  text-align: center;
  letter-spacing: 4px;
  margin: 12px 0 4px;
  position: relative;
  z-index: 1;
}
.card-master-tag {
  text-align: center;
  font-size: 13px;
  color: var(--color-gold);
  font-family: var(--font-serif);
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}
.card-aphorism {
  font-family: var(--font-serif);
  font-size: 17px;
  line-height: 1.6;
  color: var(--color-ink);
  text-align: center;
  padding: 12px 14px;
  background: rgba(255,255,255,0.7);
  border-radius: 8px;
  border: 1px solid var(--color-border);
  margin: 8px 0;
  position: relative;
  z-index: 1;
}
.card-english-motto {
  font-size: 11.5px;
  color: var(--color-muted);
  text-align: center;
  line-height: 1.4;
  margin-top: 4px;
  font-style: italic;
  position: relative;
  z-index: 1;
}
.card-bottom-bar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px dashed var(--color-border);
  position: relative;
  z-index: 1;
}
.card-meta-user {
  font-size: 12px;
  color: var(--color-ink-light);
  line-height: 1.5;
}
.card-stamp-mark {
  width: 44px;
  height: 44px;
  border-radius: 6px;
  background: linear-gradient(135deg, #A8302A 0%, #8E2927 100%);
  color: #FFF;
  font-family: var(--font-serif);
  font-size: 13px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 1px;
  box-shadow: 0 2px 6px rgba(142,41,39,0.25);
  line-height: 1.2;
  text-align: center;
  padding: 2px;
}
.card-ops-toolbar {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 14px;
}
.btn-card-action {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-ink);
  padding: 7px 14px;
  border-radius: 20px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(34,31,27,0.03);
}
.btn-card-action:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-light);
  transform: translateY(-1px);
}
.btn-card-action.primary {
  background: var(--color-primary);
  color: #FFF;
  border-color: var(--color-primary);
}
.btn-card-action.primary:hover {
  background: var(--color-primary-hover);
  color: #FFF;
}
"""

if "/* PRD 4.0 儒释道三学赛道" not in content:
    content = content.replace("</style>", CSS_INJECTION + "\n</style>", 1)
    print("[ok] Injected PRD 4.0 CSS styles")

# ---------------------------------------------------------------------------
# 2. 注入 HTML：在输入区域上方添加儒释道三学赛道选择器
# ---------------------------------------------------------------------------
TRACK_SELECTOR_HTML = """
      <!-- PRD 4.0 儒释道三学赛道与代表导师选择器 -->
      <div class="school-track-selector" id="schoolTrackSelector">
        <div class="school-track-header">
          <div class="school-track-title">选定国学修道赛道与答疑先圣</div>
          <div class="school-motto-badge" id="currentMasterMotto">先师孔子 ｜ 君子求诸己 · 仁者爱人</div>
        </div>
        <div class="school-track-pills" id="schoolTrackPills">
          <button type="button" class="school-pill active" data-track="confucianism" data-master="confucius" data-color="rgb(140, 58, 43)" data-motto="先师孔子 ｜ 君子求诸己 · 仁者爱人" data-hint="有何立身处世、责任何在、人伦日用之惑，请与夫子倾诉...">
            <span class="pill-seal">儒</span>
            <span class="pill-info">
              <span class="pill-name">儒学 · 孔子</span>
              <span class="pill-desc">入世修身 · 勇毅担当</span>
            </span>
          </button>
          <button type="button" class="school-pill" data-track="daoism" data-master="laozi" data-color="rgb(43, 76, 95)" data-motto="道家宗师 ｜ 道法自然 · 致虚守静" data-hint="有何用力过猛、身心劳形、进退难安之念，且听老君道来...">
            <span class="pill-seal">道</span>
            <span class="pill-info">
              <span class="pill-name">道学 · 老子</span>
              <span class="pill-desc">顺应自然 · 无为逍遥</span>
            </span>
          </button>
          <button type="button" class="school-pill" data-track="buddhism" data-master="shakyamuni" data-color="rgb(181, 137, 0)" data-motto="释家觉者 ｜ 明心见性 · 应无所住" data-hint="有何爱恨执念、沉没成本舍不得、无常失落之苦，请与佛陀对谈...">
            <span class="pill-seal">释</span>
            <span class="pill-info">
              <span class="pill-name">释学 · 佛陀</span>
              <span class="pill-desc">破执见性 · 慈悲解脱</span>
            </span>
          </button>
          <button type="button" class="school-pill" data-track="symposium" data-master="all" data-color="rgb(118, 55, 98)" data-motto="东方三圣 ｜ 以儒立身 · 以道养生 · 以释修心" data-hint="人生重大抉择与多重迷茫，请三圣圆桌并案会诊...">
            <span class="pill-seal">合</span>
            <span class="pill-info">
              <span class="pill-name">三圣圆桌</span>
              <span class="pill-desc">三教合参 · 圆融参悟</span>
            </span>
          </button>
        </div>
        <div class="nickname-bar">
          <span>问道者道号/称谓：</span>
          <div style="display:flex;align-items:center;gap:6px;">
            <input type="text" id="userNicknameInput" class="nickname-input" placeholder="自拟道号" value="同修" maxlength="8">
            <span style="font-size:11px;color:var(--color-muted);">（将印刻在专属解脱卡牌上）</span>
          </div>
        </div>
      </div>
"""

TARGET_ENTRY_SWITCH = '<div class="entry-switch-bar">'
if "id=\"schoolTrackSelector\"" not in content and TARGET_ENTRY_SWITCH in content:
    content = content.replace(TARGET_ENTRY_SWITCH, TRACK_SELECTOR_HTML + "\n      " + TARGET_ENTRY_SWITCH, 1)
    print("[ok] Injected schoolTrackSelector HTML")

# ---------------------------------------------------------------------------
# 3. 注入 HTML：在结果页渲染专属“解脱之道” 3D 卡牌舞台
# ---------------------------------------------------------------------------
LIBERATION_CARD_HTML = """
      <!-- PRD 4.0 专属解脱之道 3D 卡牌舞台 -->
      <div id="liberationHeroContainer" style="margin:24px 0 20px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
          <h3 style="font-family:var(--font-serif);font-size:18px;margin:0;color:var(--color-ink);display:flex;align-items:center;gap:6px;">
            <span>专属解脱之道卡牌</span>
            <span style="font-size:12px;font-weight:normal;color:var(--color-muted);">（点击卡面 3D 翻转）</span>
          </h3>
          <span id="liberationCardBadge" style="font-size:11px;background:var(--color-gold-bg);color:var(--color-gold);padding:2px 8px;border-radius:10px;border:1px solid var(--color-gold-border);">300 DPI 打印级母版已就绪</span>
        </div>

        <div class="liberation-hero-card">
          <div class="liberation-card-3d" id="liberationCard3D" onclick="toggleLiberation3DFlip()">
            <!-- 正面·道相与定心 -->
            <div class="liberation-face liberation-front" id="libCardFront">
              <div class="card-inner-frame"></div>
              <div class="card-top-id">
                <span id="lcSchoolTag">【悟堂 · 儒释道解脱之道】</span>
                <span id="lcSerialNo">WU-RU-2026-A89F</span>
              </div>
              <div style="margin:auto 0;text-align:center;">
                <div class="card-main-title" id="lcCardName">【 克 己 】</div>
                <div class="card-master-tag" id="lcMasterTag">先师孔子 垂示 ｜ 仁者爱人 · 求诸于己</div>
                <div class="card-aphorism" id="lcAphorism">君子求诸己，万般皆因行未至。立志而笃行，当下即安泰。</div>
                <div class="card-english-motto" id="lcEnglishMotto">Self-discipline brings enduring peace and true dignity.</div>
              </div>
              <div class="card-bottom-bar">
                <div class="card-meta-user">
                  <div id="lcLunarDate" style="color:var(--color-muted);">节令：丙午年 · 霜降</div>
                  <div style="font-weight:600;margin-top:2px;">求道者：<span id="lcNickname" style="color:var(--color-primary);">同修</span></div>
                </div>
                <div class="card-stamp-mark" id="lcStampMark">解脱<br>真诠</div>
              </div>
            </div>

            <!-- 背面·经典与当下功课 -->
            <div class="liberation-face liberation-back" id="libCardBack">
              <div class="card-inner-frame"></div>
              <div class="card-top-id">
                <span style="color:var(--color-primary);font-weight:700;">【解脱秘旨 · 行履功课】</span>
                <span style="color:var(--color-muted);">300 DPI 印刷规格</span>
              </div>
              <div style="margin:10px 0;font-size:12px;color:var(--color-ink-light);background:rgba(255,255,255,0.8);padding:8px 10px;border-radius:6px;border:1px solid var(--color-border);">
                <div style="font-weight:600;color:var(--color-muted);margin-bottom:2px;">【心事洞幽】</div>
                <div id="lcBackStatement" style="font-size:12px;line-height:1.4;">心事多有内耗与纠结，求一份定心法门。</div>
              </div>
              <div style="margin:8px 0;font-size:12px;background:rgba(255,255,255,0.9);padding:10px;border-radius:8px;border:1px solid var(--color-gold-border);">
                <div style="font-weight:700;color:var(--color-gold);margin-bottom:3px;" id="lcBackClassicSource">《论语·卫灵公》（春秋·孔子）</div>
                <div style="font-family:var(--font-serif);font-size:13.5px;color:var(--color-ink);line-height:1.5;margin-bottom:4px;" id="lcBackQuote">「君子求诸己，小人求诸人。」</div>
                <div style="font-size:11.5px;color:var(--color-muted);line-height:1.4;" id="lcBackInterp">遇到不顺先看自己能做什么，把力气收回到自己身上，是瓦解内耗的唯一解药。</div>
              </div>
              <div style="margin-top:auto;font-size:12px;background:rgba(240,246,242,0.9);padding:8px 10px;border-radius:8px;border:1px solid rgba(58,109,79,0.2);">
                <div style="font-weight:700;color:#2B6E3F;margin-bottom:3px;" id="lcBackActionTitle">【今晚 5 分钟微功课】</div>
                <div style="font-size:11.5px;color:var(--color-ink-light);line-height:1.4;" id="lcBackActionSteps">闭目静坐深呼吸三次，在便签写下1件眼前可控之事并立刻动手完成。</div>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;padding-top:6px;border-top:1px dashed var(--color-border);font-size:10.5px;color:var(--color-muted);">
                <span>悟堂·儒释道卡牌人生</span>
                <span>TCG Standard 63x88mm</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 专属卡牌动作栏 -->
        <div class="card-ops-toolbar">
          <button type="button" class="btn-card-action" onclick="toggleLiberation3DFlip()">
            <span>🔄 翻转卡面</span>
          </button>
          <button type="button" class="btn-card-action primary" id="btnExportPrintPack" onclick="exportCurrentPrintPack()">
            <span>🖨️ 导出 300DPI 实体打印包 (送印级)</span>
          </button>
          <button type="button" class="btn-card-action" id="btnSaveWallpaper" onclick="downloadCardWallpaper()">
            <span>📱 保存手机高清壁纸</span>
          </button>
          <button type="button" class="btn-card-action" onclick="showToast('已收入您的「儒释道卡牌人生」典藏图鉴！')">
            <span>📜 珍藏入册</span>
          </button>
        </div>
      </div>
"""

TARGET_FOUR_STEP_HEADING = '<!-- F-05 四步解忧方完整结构 -->'
if "id=\"liberationHeroContainer\"" not in content and TARGET_FOUR_STEP_HEADING in content:
    content = content.replace(TARGET_FOUR_STEP_HEADING, LIBERATION_CARD_HTML + "\n\n      " + TARGET_FOUR_STEP_HEADING, 1)
    print("[ok] Injected liberationHeroContainer HTML")

# ---------------------------------------------------------------------------
# 4. 注入 JavaScript 逻辑（在 </script> 之前）
# ---------------------------------------------------------------------------
JS_INJECTION = """
  // ==========================================================================
  // PRD 4.0 儒释道三学赛道、专属解脱卡牌与实体打印交互引擎
  // ==========================================================================
  appState.selectedTrack = 'confucianism';
  appState.selectedMaster = 'confucius';
  appState.userNickname = '同修';
  appState.currentCardSignature = null;

  function initSchoolTrackSelector() {
    var pills = document.querySelectorAll('#schoolTrackPills .school-pill');
    var mottoEl = $('currentMasterMotto');
    var textarea = $('userTextarea');
    var nickInput = $('userNicknameInput');

    if (nickInput) {
      nickInput.oninput = function() {
        appState.userNickname = nickInput.value.trim() || '同修';
      };
    }

    pills.forEach(function(pill) {
      pill.onclick = function() {
        pills.forEach(function(p) { p.classList.remove('active'); });
        pill.classList.add('active');
        appState.selectedTrack = pill.getAttribute('data-track');
        appState.selectedMaster = pill.getAttribute('data-master');

        var motto = pill.getAttribute('data-motto');
        var hint = pill.getAttribute('data-hint');
        if (mottoEl && motto) mottoEl.textContent = motto;
        if (textarea && hint) textarea.setAttribute('placeholder', hint);
      };
    });
  }

  function toggleLiberation3DFlip() {
    var card = $('liberationCard3D');
    if (card) {
      card.classList.toggle('is-flipped');
    }
  }

  function updateLiberationCardView(sig) {
    if (!sig) return;
    appState.currentCardSignature = sig;

    if ($('lcCardName')) $('lcCardName').textContent = '【 ' + (sig.card_name || '明德') + ' 】';
    if ($('lcMasterTag')) $('lcMasterTag').textContent = (sig.master || '先圣') + ' 垂示 ｜ ' + (sig.aphorism ? sig.aphorism.slice(0, 16) : '立足东方智慧');
    if ($('lcAphorism')) $('lcAphorism').textContent = sig.aphorism || '君子求诸己，万般皆因行未至。';
    if ($('lcEnglishMotto')) $('lcEnglishMotto').textContent = sig.english_mantra || 'Self-discipline brings enduring peace.';
    if ($('lcNickname')) $('lcNickname').textContent = appState.userNickname || '同修';
    if ($('lcSerialNo')) {
      var sch = (sig.school || 'RU').slice(0, 3).toUpperCase();
      $('lcSerialNo').textContent = 'WU-' + sch + '-' + (new Date().getFullYear()) + '-' + Math.random().toString(36).substring(2, 6).toUpperCase();
    }

    if ($('lcBackStatement')) {
      var t = $('userTextarea') ? $('userTextarea').value.trim() : '';
      $('lcBackStatement').textContent = t ? (t.length > 50 ? t.slice(0, 50) + '...' : t) : '心事多有内耗与纠结，求一份定心法门。';
    }
    if ($('lcBackClassicSource')) $('lcBackClassicSource').textContent = sig.classic_source || '《论语·卫灵公》（春秋·孔子）';
    if ($('lcBackQuote')) $('lcBackQuote').textContent = '「' + (sig.quote || '君子求诸己，小人求诸人。') + '」';
    if ($('lcBackInterp')) $('lcBackInterp').textContent = sig.interpretation || '把力气用在自己身上，是内耗的唯一解药。';
    if ($('lcBackActionTitle')) $('lcBackActionTitle').textContent = '【' + (sig.action_title || '当下 5 分钟微功课') + '】';
    if ($('lcBackActionSteps')) {
      var steps = sig.action_steps || ['闭目静坐呼吸三次', '记录当下可控之事'];
      $('lcBackActionSteps').textContent = steps.join('；');
    }
  }

  function exportCurrentPrintPack() {
    var sig = appState.currentCardSignature;
    if (!sig) {
      showToast('正在为您生成解脱卡印，请稍候...');
      return;
    }
    showToast('正在打包 300 DPI 实体卡牌印刷文件...');
    var payload = {
      card_id: sig.card_name || '001',
      school: sig.school || appState.selectedTrack || 'confucianism',
      master: sig.master || '孔子',
      name: sig.card_name || '明德',
      aphorism: sig.aphorism || '君子求诸己，万般皆因行未至。',
      english_mantra: sig.english_mantra || 'Self-discipline brings peace.',
      user_statement: $('userTextarea') ? $('userTextarea').value.trim() : '',
      user_nickname: appState.userNickname || '同修',
      lunar_date: '丙午年 · 霜降',
      classic_source: sig.classic_source || '',
      quote: sig.quote || '',
      interpretation: sig.interpretation || '',
      action_title: sig.action_title || '静坐调息',
      action_steps: sig.action_steps || ['深呼吸三次', '记录眼下可控之事']
    };

    fetch('http://localhost:8000/api/card/export-print-pack', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(function(res) {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.blob();
    }).then(function(blob) {
      var url = window.URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = '悟堂解脱卡-' + (sig.card_name || '明德') + '-300DPI-印刷包.zip';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      showToast('300 DPI 实体打印包下载已完成！可直接送数码快印店下料。');
    }).catch(function(err) {
      showToast('调用后台打包异常，降级通过本地生成打印版');
      window.print();
    });
  }

  function downloadCardWallpaper() {
    showToast('正在导出手机壁纸...');
    var sig = appState.currentCardSignature || {};
    var canvas = document.createElement('canvas');
    canvas.width = 1080;
    canvas.height = 1920;
    var ctx = canvas.getContext('2d');

    // 背景暖宣白渐变
    var grad = ctx.createLinearGradient(0, 0, 0, 1920);
    grad.addColorStop(0, '#FAF7EF');
    grad.addColorStop(1, '#F0EAE0');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 1080, 1920);

    // 边框金线
    ctx.strokeStyle = '#9F7430';
    ctx.lineWidth = 3;
    ctx.strokeRect(60, 60, 960, 1800);
    ctx.strokeStyle = '#D4CBBD';
    ctx.lineWidth = 1;
    ctx.strokeRect(80, 80, 920, 1760);

    // 标题
    ctx.fillStyle = '#8E2927';
    ctx.font = 'bold 84px serif';
    ctx.textAlign = 'center';
    ctx.fillText('【 ' + (sig.card_name || '明德') + ' 】', 540, 520);

    ctx.fillStyle = '#9F7430';
    ctx.font = '36px serif';
    ctx.fillText((sig.master || '先圣') + ' 垂示 ｜ 东方解脱之道', 540, 640);

    // 定心偈
    ctx.fillStyle = '#221F1B';
    ctx.font = '46px serif';
    var aph = sig.aphorism || '君子求诸己，万般皆因行未至。';
    ctx.fillText(aph, 540, 900);

    // 英文
    ctx.fillStyle = '#7E7870';
    ctx.font = '28px sans-serif';
    ctx.fillText(sig.english_mantra || 'Self-discipline brings enduring peace.', 540, 980);

    // 底栏
    ctx.font = '30px serif';
    ctx.fillStyle = '#4D463E';
    ctx.fillText('求道者：' + (appState.userNickname || '同修') + '   丙午年·霜降', 540, 1680);
    ctx.font = '24px sans-serif';
    ctx.fillStyle = '#999';
    ctx.fillText('悟堂 · 儒释道卡牌人生', 540, 1740);

    var url = canvas.toDataURL('image/png');
    var a = document.createElement('a');
    a.href = url;
    a.download = '悟堂壁纸-' + (sig.card_name || '解脱之道') + '.png';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast('高清壁纸已保存至本地相册！');
  }
"""

if "initSchoolTrackSelector" not in content:
    # 注入到 window.addEventListener('DOMContentLoaded') 内部或脚本尾部
    content = content.replace("  // 页面入口路由分发", JS_INJECTION + "\n\n  // 页面入口路由分发", 1)
    print("[ok] Injected PRD 4.0 JavaScript engine")

# ---------------------------------------------------------------------------
# 5. 更新 fetch body：在 relief/stream 调用时传入 track/master/nickname
# ---------------------------------------------------------------------------
OLD_FETCH_BODY = "body: JSON.stringify({ text: text, scenario: sc, case_id: caseId }),"
NEW_FETCH_BODY = """body: JSON.stringify({
        text: text,
        scenario: sc,
        case_id: caseId,
        track: appState.selectedTrack || 'confucianism',
        master: appState.selectedMaster || 'confucius',
        user_nickname: appState.userNickname || '同修'
      }),"""

if OLD_FETCH_BODY in content:
    content = content.replace(OLD_FETCH_BODY, NEW_FETCH_BODY, 1)
    print("[ok] Updated fetch body with track, master, and user_nickname")

# ---------------------------------------------------------------------------
# 6. 处理 SSE card_signature 接收并自动渲染解脱卡牌
# ---------------------------------------------------------------------------
SSE_TOKEN_HANDLER = "if (data.type === 'token') {"
NEW_SSE_TOKEN_HANDLER = """if (data.type === 'card_signature') {
                updateLiberationCardView(data.data);
              } else if (data.type === 'token') {"""

if SSE_TOKEN_HANDLER in content and "data.type === 'card_signature'" not in content:
    content = content.replace(SSE_TOKEN_HANDLER, NEW_SSE_TOKEN_HANDLER, 1)
    print("[ok] Added SSE card_signature receiver")

# ---------------------------------------------------------------------------
# 7. 更新 updateStreamingFourStep 支持 4.0 标题识别
# ---------------------------------------------------------------------------
OLD_STEP_RECOG = """      if (l.indexOf('01 听见了') !== -1) { current = '01'; continue; }
      if (l.indexOf('02 古人有云') !== -1) { current = '02'; continue; }
      if (l.indexOf('03 试试这一招') !== -1) { current = '03'; continue; }
      if (l.indexOf('04 读这一段') !== -1) { current = '04'; continue; }"""

NEW_STEP_RECOG = """      if (l.indexOf('01 听见了') !== -1 || l.indexOf('闻心') !== -1) { current = '01'; continue; }
      if (l.indexOf('02 古人有云') !== -1 || l.indexOf('示道') !== -1) { current = '02'; continue; }
      if (l.indexOf('03 试试这一招') !== -1 || l.indexOf('笃行') !== -1) { current = '03'; continue; }
      if (l.indexOf('04 读这一段') !== -1 || l.indexOf('法印') !== -1) { current = '04'; continue; }"""

if OLD_STEP_RECOG in content:
    content = content.replace(OLD_STEP_RECOG, NEW_STEP_RECOG, 1)
    print("[ok] Updated updateStreamingFourStep with 4.0 headings")

# ---------------------------------------------------------------------------
# 8. 更新 DOMContentLoaded 初始化调用 initSchoolTrackSelector
# ---------------------------------------------------------------------------
if "initSchoolTrackSelector();" not in content and "bindGlobalEvents();" in content:
    content = content.replace("bindGlobalEvents();", "bindGlobalEvents();\n    initSchoolTrackSelector();", 1)
    print("[ok] Added initSchoolTrackSelector() call on DOMContentLoaded")

# 写回模板
with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"[success] Updated {TEMPLATE_PATH}! Size: {len(content)} bytes")
