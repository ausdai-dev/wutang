# -*- coding: utf-8 -*-
"""
Patch frontend/_template.html to integrate:
1. Resonant 96 Zen Awareness Card Section (【借境观心 · 契合心象画卷】)
2. Card CSS styles
3. Interactive JS engine for track selector, 3D liberation flip, 96-card resonance matching,
   journal prefill, and favorite collection.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "frontend" / "_template.html"

def main():
    content = TEMPLATE_PATH.read_text(encoding="utf-8")
    print(f"Initial template length: {len(content)} chars")

    # 1. 注入 CSS (在 </style> 之前)
    RESONANT_CSS = """
/* ==========================================================================
   PRD 4.1 借境观心 · 契合心象画卷 (96张典藏觉察牌联动)
   ========================================================================== */
.resonant-card-section {
  margin: 32px 0 24px;
  animation: fadeIn 0.5s ease-out;
}
.resonant-card-card {
  background: rgba(253, 251, 247, 0.96);
  border: 1px solid #D9CEBD;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 10px 28px rgba(44, 40, 37, 0.06);
  display: flex;
  gap: 22px;
  align-items: stretch;
  position: relative;
  overflow: hidden;
}
.resonant-card-image-box {
  width: 170px;
  min-width: 170px;
  aspect-ratio: 2 / 3;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  border: 1.5px solid #C4A47C;
  box-shadow: 0 6px 18px rgba(44, 40, 37, 0.12);
  cursor: pointer;
  background: #EAE4D8;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.resonant-card-image-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(44, 40, 37, 0.2);
}
.resonant-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.resonant-card-img-hint {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(42, 38, 35, 0.75);
  color: #FFF;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  backdrop-filter: blur(4px);
  white-space: nowrap;
  pointer-events: none;
}
.resonant-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}
.resonant-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 10px;
  border-bottom: 1px dashed #E2DACB;
  padding-bottom: 8px;
}
.resonant-card-series {
  font-size: 11.5px;
  background: #EBF3ED;
  color: #2B6E3F;
  border: 1px solid rgba(43, 110, 63, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
  margin-right: 6px;
}
.resonant-card-no {
  font-size: 11.5px;
  color: #7E7870;
  font-family: monospace;
}
.resonant-card-title {
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 700;
  color: #8E2927;
  margin: 0;
  letter-spacing: 2px;
}
.resonant-card-core-box,
.resonant-card-question-box,
.resonant-card-reason-box {
  margin-bottom: 8px;
  line-height: 1.55;
}
.rc-label {
  font-size: 11.5px;
  font-weight: 700;
  color: #7A736C;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}
.rc-core-text {
  font-family: var(--font-serif);
  font-size: 14.5px;
  color: var(--color-ink);
  font-weight: 600;
}
.rc-question-text {
  font-size: 13.5px;
  color: #2B6E3F;
  background: rgba(235, 243, 237, 0.5);
  border-left: 3px solid #2B6E3F;
  padding: 5px 10px;
  border-radius: 0 4px 4px 0;
}
.rc-reason-text {
  font-size: 12.5px;
  color: #6A635B;
  font-style: italic;
}
.resonant-card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #E2DACB;
}
.btn-rc-action {
  background: #FFF;
  border: 1px solid #D9CEBD;
  color: #4A443E;
  padding: 6px 12px;
  border-radius: 18px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
}
.btn-rc-action:hover {
  border-color: #8E2927;
  color: #8E2927;
  background: #FAF5F5;
  transform: translateY(-1px);
}
.btn-rc-action.primary {
  background: #2B6E3F;
  color: #FFF;
  border-color: #2B6E3F;
}
.btn-rc-action.primary:hover {
  background: #235B34;
  color: #FFF;
}
@media (max-width: 640px) {
  .resonant-card-card {
    flex-direction: column;
    align-items: center;
  }
  .resonant-card-image-box {
    width: 200px;
  }
}
"""
    if "resonant-card-section" not in content:
        content = content.replace("</style>", RESONANT_CSS + "\n</style>", 1)
        print("[ok] Injected resonant card CSS")

    # 2. 注入 HTML：位于 liberationHeroContainer 之后，四步解忧方之前
    RESONANT_HTML = """
      <!-- PRD 4.1 借境观心 · 契合心象画卷 (96张典藏觉察牌联动) -->
      <div id="resonantZenCardContainer" class="resonant-card-section hidden">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
          <h3 style="font-family:var(--font-serif);font-size:18px;margin:0;color:var(--color-ink);display:flex;align-items:center;gap:6px;">
            <span>🖼️ 借境观心 · 契合心象画卷</span>
            <span style="font-size:12px;font-weight:normal;color:var(--color-muted);">先圣映照的当下意象</span>
          </h3>
          <span style="font-size:11px;background:#EBF3ED;color:#2B6E3F;padding:2px 8px;border-radius:10px;border:1px solid rgba(43,110,63,0.2);">96 典藏画廊 · 心象共振</span>
        </div>

        <div class="resonant-card-card">
          <!-- 左侧：2:3 纵向水墨大图，可点击查看大图 -->
          <div class="resonant-card-image-box" onclick="handleViewInGallery()" title="点击赏析大图">
            <img id="rcImage" src="" alt="" class="resonant-card-img" />
            <div class="resonant-card-img-hint">点击赏析大图</div>
          </div>

          <!-- 右侧：卡牌意境与深度叩问 -->
          <div class="resonant-card-body">
            <div class="resonant-card-header">
              <div>
                <span class="resonant-card-series" id="rcSeries">禅心之境</span>
                <span class="resonant-card-no" id="rcNum">WUTANG-CARD-03 · 03</span>
              </div>
              <h4 class="resonant-card-title" id="rcName">留白</h4>
            </div>

            <!-- 核心觉察 -->
            <div class="resonant-card-core-box">
              <div class="rc-label">【核心觉察】</div>
              <div class="rc-core-text" id="rcCore">不必把每一处空缺都立即填满。</div>
            </div>

            <!-- 叩问心门 -->
            <div class="resonant-card-question-box">
              <div class="rc-label">【叩问心门】</div>
              <div class="rc-question-text" id="rcQuestion">你是否允许自己暂时不知道答案？</div>
            </div>

            <!-- 契合之由 -->
            <div class="resonant-card-reason-box" id="rcReasonBox">
              <div class="rc-label">【为何契合】</div>
              <div class="rc-reason-text" id="rcReason">此幅水墨山水留白极多，正映照你此刻心绪繁杂，宜暂停抓取，给心神留一分吐纳之地。</div>
            </div>

            <!-- 动作按钮栏 -->
            <div class="resonant-card-actions">
              <button type="button" class="btn-rc-action primary" id="btnJournalWithResonantCard" onclick="handleJournalWithResonantCard()">
                <span>✍️ 以此牌写觉察日记</span>
              </button>
              <button type="button" class="btn-rc-action" id="btnCollectResonantCard" onclick="handleCollectResonantCard()">
                <span id="btnCollectResonantCardText">⭐ 收入珍藏</span>
              </button>
              <button type="button" class="btn-rc-action" id="btnViewInGallery" onclick="handleViewInGallery()">
                <span>🔍 在 96 画廊中研读</span>
              </button>
            </div>
          </div>
        </div>
      </div>
"""
    TARGET_CONTAINER = '<!-- 专属卡牌动作栏 -->'
    if "id=\"resonantZenCardContainer\"" not in content:
        # 寻找 liberationHeroContainer 结尾的 </div>
        idx = content.find("id=\"liberationHeroContainer\"")
        if idx != -1:
            end_div_idx = content.find("</div>\n\n\n      <!-- F-05 四步解忧方完整结构 -->", idx)
            if end_div_idx != -1:
                content = content[:end_div_idx + 6] + "\n" + RESONANT_HTML + content[end_div_idx + 6:]
                print("[ok] Injected resonant card HTML after liberationHeroContainer")
            else:
                # 尝试用四步解忧方作为定位锚点
                content = content.replace("<!-- F-05 四步解忧方完整结构 -->", RESONANT_HTML + "\n\n      <!-- F-05 四步解忧方完整结构 -->", 1)
                print("[ok] Injected resonant card HTML before fourStep")

    # 3. 注入交互逻辑 JavaScript
    RESONANT_JS = """
  // ==========================================================================
  // PRD 4.0 & 4.1 儒释道三学赛道、专属解脱卡牌与 96 觉察牌心象共振引擎
  // ==========================================================================
  appState.selectedTrack = 'confucianism';
  appState.selectedMaster = 'confucius';
  appState.userNickname = '同修';
  appState.currentCardSignature = null;
  var currentResonantZenCard = null;

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

    // 联动 96 张画廊：寻找并呈现最契合的心象觉察牌
    updateResonantZenCard(sig.matched_zen_card, sig);
  }

  function findClientResonantZenCard(userText, track, cardSig) {
    var cardsList = (typeof ZEN_CARDS_96 !== 'undefined' && ZEN_CARDS_96 && ZEN_CARDS_96.length) ? ZEN_CARDS_96 : ((typeof RAW_DATA !== 'undefined' && RAW_DATA.zenCards96) ? RAW_DATA.zenCards96 : []);
    if (!cardsList || !cardsList.length) return null;

    if (cardSig && cardSig.matched_zen_card && cardSig.matched_zen_card.card_id) {
      return cardSig.matched_zen_card;
    }

    var text = (userText || '') + ' ' + (cardSig ? (cardSig.card_name || '') + ' ' + (cardSig.aphorism || '') : '');
    var trackKey = (track || appState.selectedTrack || 'confucianism').toLowerCase();

    // 牌名同名优先匹配
    var targetName = (cardSig && cardSig.card_name) ? cardSig.card_name.trim() : '';
    if (targetName) {
      for (var i = 0; i < cardsList.length; i++) {
        var c = cardsList[i];
        if (c.name === targetName || (targetName.length >= 2 && c.name.indexOf(targetName) !== -1)) {
          var copy = Object.assign({}, c);
          copy.match_reason = '先圣以「' + c.name + '」为法印，此幅水墨画卷恰好映照出此等静心气象。';
          return copy;
        }
      }
    }

    // 语义多维共振打分
    var targetSeries = '君子修身';
    if (trackKey.indexOf('dao') !== -1 || trackKey.indexOf('道') !== -1) targetSeries = '道法自然';
    else if (trackKey.indexOf('bud') !== -1 || trackKey.indexOf('释') !== -1 || trackKey.indexOf('佛') !== -1) targetSeries = '禅心之境';
    else if (trackKey.indexOf('sym') !== -1 || trackKey.indexOf('圆桌') !== -1) targetSeries = '禅心之境';

    var bestCard = null;
    var maxScore = -1;

    for (var j = 0; j < cardsList.length; j++) {
      var card = cardsList[j];
      var score = 0;

      if (card.series === targetSeries) score += 4;
      if (text.match(/[累忙慢歇烦急紧压力]/) && card.series === '一盏茶事') score += 3.5;
      if (text.match(/[关系朋友父母伴侣拒绝讨好边界]/) && card.series === '因缘相惜') score += 3.5;
      if (text.match(/[迷茫未来选择低谷远方方向]/) && card.series === '山水人生') score += 3.5;

      if (text.indexOf(card.name) !== -1) score += 3;
      if (card.core) {
        var keywords = card.core.split(/[，。、\s]/);
        for (var k = 0; k < keywords.length; k++) {
          if (keywords[k].length >= 2 && text.indexOf(keywords[k]) !== -1) score += 2;
        }
      }

      if (score > maxScore) {
        maxScore = score;
        bestCard = card;
      }
    }

    if (!bestCard) bestCard = cardsList[0];
    var matched = Object.assign({}, bestCard);
    matched.match_reason = '你倾诉中心绪多有牵挂与紧绷，此幅《' + matched.name + '》正契合当下心象，助你借境观心：' + (matched.core || '');
    return matched;
  }

  function updateResonantZenCard(matchedCard, sig) {
    var card = matchedCard;
    if (!card) {
      var userText = $('userTextarea') ? $('userTextarea').value.trim() : '';
      card = findClientResonantZenCard(userText, appState.selectedTrack, sig);
    }
    if (!card) return;

    currentResonantZenCard = card;

    var container = $('resonantZenCardContainer');
    if (!container) return;

    if ($('rcImage')) {
      $('rcImage').src = card.image_png || card.image_jpg || ('assets/cards/images/' + card.num + '_' + card.name + '.png');
      $('rcImage').alt = card.name || '心象画卷';
    }
    if ($('rcSeries')) $('rcSeries').textContent = card.series || '东方意象';
    if ($('rcNum')) $('rcNum').textContent = (card.card_id || ('WUTANG-CARD-' + card.num)) + ' · ' + (card.num || '01');
    if ($('rcName')) $('rcName').textContent = card.name || '静观';
    if ($('rcCore')) $('rcCore').textContent = card.core || '暂停评判，先看见正在发生的事。';
    if ($('rcQuestion')) $('rcQuestion').textContent = card.question || '如果先不急着评判，你此刻真正看见了什么？';
    if ($('rcReason')) $('rcReason').textContent = card.match_reason || ('先圣洞幽：以此《' + (card.name || '') + '》山水意境映照当下，助你明心破执。');

    // 检查是否已收藏
    var favs = getStorageJson('wutang_favorite_cards', []);
    var isFav = favs.some(function(f) { return f.card_id === card.card_id || f.name === card.name; });
    var favBtnText = $('btnCollectResonantCardText');
    if (favBtnText) {
      favBtnText.textContent = isFav ? '✓ 已收入珍藏' : '⭐ 收入珍藏';
    }

    container.classList.remove('hidden');
  }

  function handleJournalWithResonantCard() {
    if (!currentResonantZenCard) return;
    var card = currentResonantZenCard;

    if (typeof switchMainTab === 'function') {
      switchMainTab('growth');
    }

    var journalInput = $('journalInputText');
    if (journalInput) {
      journalInput.value = '【借境观心 · ' + card.name + '】\\n' +
        '核心觉察：' + card.core + '\\n' +
        '叩问心门：' + (card.question || '') + '\\n\\n' +
        '我的当下心声：\\n';
      journalInput.focus();
      journalInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    showToast('已载入《' + card.name + '》觉察课题，请写下您的真实心声。');
  }

  function handleCollectResonantCard() {
    if (!currentResonantZenCard) return;
    var card = currentResonantZenCard;
    var favs = getStorageJson('wutang_favorite_cards', []);
    var idx = favs.findIndex(function(f) { return f.card_id === card.card_id || f.name === card.name; });

    if (idx >= 0) {
      favs.splice(idx, 1);
      setStorageJson('wutang_favorite_cards', favs);
      if ($('btnCollectResonantCardText')) $('btnCollectResonantCardText').textContent = '⭐ 收入珍藏';
      showToast('已从珍藏中移出《' + card.name + '》');
    } else {
      favs.unshift({
        card_id: card.card_id,
        name: card.name,
        series: card.series,
        core: card.core,
        question: card.question,
        image_png: card.image_png,
        saved_at: new Date().toISOString()
      });
      setStorageJson('wutang_favorite_cards', favs);
      if ($('btnCollectResonantCardText')) $('btnCollectResonantCardText').textContent = '✓ 已收入珍藏';
      showToast('已将《' + card.name + '》收入您的「儒释道卡牌人生」典藏画卷！');
    }
  }

  function handleViewInGallery() {
    if (!currentResonantZenCard) return;
    if (typeof openZen96CardModal === 'function') {
      openZen96CardModal(currentResonantZenCard.card_id);
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

  // 暴露到 window
  window.toggleLiberation3DFlip = toggleLiberation3DFlip;
  window.updateLiberationCardView = updateLiberationCardView;
  window.updateResonantZenCard = updateResonantZenCard;
  window.handleJournalWithResonantCard = handleJournalWithResonantCard;
  window.handleCollectResonantCard = handleCollectResonantCard;
  window.handleViewInGallery = handleViewInGallery;
  window.exportCurrentPrintPack = exportCurrentPrintPack;
  window.downloadCardWallpaper = downloadCardWallpaper;
"""
    if "initSchoolTrackSelector" not in content:
        # 放在 bootstrap 之前
        content = content.replace("  function bootstrap() {", RESONANT_JS + "\n\n  function bootstrap() {", 1)
        print("[ok] Injected PRD 4.0 & 4.1 JavaScript engine before bootstrap()")

    # 4. 在 bootstrap() 中调用 initSchoolTrackSelector
    if "initSchoolTrackSelector();" not in content:
        content = content.replace("bgmEngine.init();", "bgmEngine.init();\n    initSchoolTrackSelector();", 1)
        print("[ok] Added initSchoolTrackSelector() in bootstrap()")

    # 5. 在 SSE reader 循环中处理 card_signature
    if "data.type === 'card_signature'" not in content and "if (evt.type === 'token') {" in content:
        content = content.replace(
            "if (evt.type === 'token') {",
            "if (evt.type === 'card_signature') {\n                  updateLiberationCardView(evt.data);\n                } else if (evt.type === 'token') {",
            1
        )
        print("[ok] Hooked SSE card_signature receiver")

    # 写回文件
    TEMPLATE_PATH.write_text(content, encoding="utf-8")
    print(f"[success] Template updated! New size: {len(content)} chars")

if __name__ == "__main__":
    main()
