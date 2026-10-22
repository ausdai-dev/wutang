# -*- coding: utf-8 -*-
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_path = os.path.join(ROOT, "frontend", "_template.html")

with open(template_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update zen-tea-banner to include 96 Zen Wisdom Pouch quick-draw button
old_banner = """          <div class="zen-banner-caption">
            <span>煮一盏清茶 · 听心底回响</span>
            <span class="zen-banner-sub">让古老智慧，温和接纳真实的你</span>
          </div>"""

new_banner = """          <div class="zen-banner-caption">
            <span>煮一盏清茶 · 听心底回响</span>
            <span class="zen-banner-sub">让古老智慧，温和接纳真实的你</span>
            <div style="margin-top:8px;">
              <button class="btn sm" id="btnDrawZenWisdom" onclick="drawRandomZen96Card()" style="background:rgba(217,119,6,0.3);border:1px solid rgba(253,230,138,0.6);color:#FDE68A;backdrop-filter:blur(6px);font-size:12px;padding:4px 14px;border-radius:20px;cursor:pointer;display:inline-flex;align-items:center;gap:6px;transition:all 0.2s ease;">
                <span>🍵 遇事不决？抽取今日东方锦囊/禅签 →</span>
              </button>
            </div>
          </div>"""

assert old_banner in text, "old_banner not found!"
text = text.replace(old_banner, new_banner, 1)

# 2. Update getAwarenessCardObj and renderAwarenessCard to strictly use CARDS_MINDSET
old_func_block = """    // 获取当前觉察牌对象 (兼容 96 张东方觉察牌与基础卡牌)
  function getAwarenessCardObj() {
    if (ZEN_CARDS_96 && ZEN_CARDS_96.length) {
      var idx = Math.abs(appState.awarenessIndex) % ZEN_CARDS_96.length;
      var z = ZEN_CARDS_96[idx];
      return {
        card_id: z.card_id,
        title: z.name,
        name: z.name,
        core: z.core,
        series: z.series,
        quote: z.core,
        front_text: z.core,
        question: z.question,
        follow_up_question: z.question,
        scenarios: z.scenarios || ['work', 'emotion']
      };
    }
    if (CARDS_MINDSET && CARDS_MINDSET.length) {
      var idx = Math.abs(appState.awarenessIndex) % CARDS_MINDSET.length;
      return CARDS_MINDSET[idx];
    }
    return { title: '当下', name: '当下', core: '安住当下', question: '静观当下，细细觉察。' };
  }

  function handleClientAwarenessCard() {
    switchMainTab('relief');
    switchClientView('userHome');
    if ($('entryBtnCard')) $('entryBtnCard').click();
  }

// ================= 觉察牌卡面渲染 (PRD 2.0 F-02) =================
  function renderAwarenessCard(idx) {
    if (ZEN_CARDS_96 && ZEN_CARDS_96.length) {
      var i = Math.abs(idx) % ZEN_CARDS_96.length;
      var c96 = ZEN_CARDS_96[i];
      if ($('awFrontTitle')) $('awFrontTitle').textContent = c96.name;
      if ($('awFrontQuestion')) $('awFrontQuestion').textContent = c96.core ? ('“' + c96.core + '”') : '';
      if ($('awFrontDesc')) $('awFrontDesc').textContent = '【' + c96.series + ' · ' + c96.num + '】 ' + (c96.question || '静观当下，细细觉察。');
      if ($('awFollowupText')) {
        $('awFollowupText').textContent = c96.question || '如果把这件事换一个视角，你觉得关键转机在哪里？';
      }
      var cardBox = $('awarenessCardBox');
      if (cardBox) {
        cardBox.classList.remove('is-flipped');
        var frontEl = cardBox.querySelector('.awareness-card-front');
        if (frontEl) {
          frontEl.style.backgroundImage = 'url(' + c96.image_png + ')';
          frontEl.style.backgroundSize = 'cover';
          frontEl.style.backgroundPosition = 'center';
          frontEl.style.border = 'none';
        }
      }
      if ($('awFollowupBox')) $('awFollowupBox').classList.add('hidden');
      if ($('awProceedWrap')) $('awProceedWrap').classList.add('hidden');
      appState.awarenessFlipped = false;
      return;
    }
    if (!CARDS_MINDSET.length) return;
    var i = Math.abs(idx) % CARDS_MINDSET.length;
    var card = CARDS_MINDSET[i];
    var qText = card.front_text || card.quote || '';
    if ($('awFrontTitle')) $('awFrontTitle').textContent = card.title || '';
    if ($('awFrontQuestion')) $('awFrontQuestion').textContent = qText ? ('「' + qText + '」') : '';
    if ($('awFrontDesc')) $('awFrontDesc').textContent = card.short_description || card.sample_prompt || card.subtitle || '静观当下，自我关照';
    if ($('awFollowupText')) {
      $('awFollowupText').textContent = card.follow_up_question || card.sample_prompt || '最近有没有一件事，让你有类似的心情？写下一句话：';
    }
    var cardBox = $('awarenessCardBox');
    if (cardBox) {
      cardBox.classList.remove('is-flipped');
      var frontEl = cardBox.querySelector('.awareness-card-front');
      if (frontEl) {
        frontEl.style.backgroundImage = 'url(' + getCardAsset('card_mindset', 'front') + ')';
        frontEl.style.backgroundSize = '100% 100%';
        frontEl.style.backgroundRepeat = 'no-repeat';
        frontEl.style.border = 'none';
      }
    }
    if ($('awFollowupBox')) $('awFollowupBox').classList.add('hidden');
    if ($('awProceedWrap')) $('awProceedWrap').classList.add('hidden');
    appState.awarenessFlipped = false;
  }"""

new_func_block = """  // 获取当前觉察牌对象 (PRD 2.0 / Option A: 还原为真实成人内心情绪觉察牌)
  function getAwarenessCardObj() {
    if (CARDS_MINDSET && CARDS_MINDSET.length) {
      var idx = Math.abs(appState.awarenessIndex) % CARDS_MINDSET.length;
      return CARDS_MINDSET[idx];
    }
    return { title: '总想让所有人满意', name: '总想让所有人满意', front_text: '我是不是很久没有认真问过自己，真正想要的是什么？', short_description: '自我反思提示卡', question: '最近有没有一件事，你其实不愿意做，却因为担心别人失望而答应了？' };
  }

  function handleClientAwarenessCard() {
    switchMainTab('relief');
    switchClientView('userHome');
    if ($('entryBtnCard')) $('entryBtnCard').click();
  }

  // ================= 觉察牌卡面渲染 (PRD 2.0 F-02: 专注于心境困扰照见) =================
  function renderAwarenessCard(idx) {
    if (!CARDS_MINDSET || !CARDS_MINDSET.length) return;
    var i = Math.abs(idx) % CARDS_MINDSET.length;
    var card = CARDS_MINDSET[i];
    var qText = card.front_text || card.quote || '';
    if ($('awFrontTitle')) $('awFrontTitle').textContent = card.title || '';
    if ($('awFrontQuestion')) $('awFrontQuestion').textContent = qText ? ('「' + qText + '」') : '';
    if ($('awFrontDesc')) $('awFrontDesc').textContent = card.short_description || card.sample_prompt || card.subtitle || '这是一张用于自我反思的提示卡，不代表对你的判断。';
    if ($('awFollowupText')) {
      $('awFollowupText').textContent = card.follow_up_question || card.sample_prompt || '最近有没有一件事，让你产生了类似的心情？写下一两句话…';
    }
    var cardBox = $('awarenessCardBox');
    if (cardBox) {
      cardBox.classList.remove('is-flipped');
      var frontEl = cardBox.querySelector('.awareness-card-front');
      if (frontEl) {
        frontEl.style.backgroundImage = 'url(' + getCardAsset('card_mindset', 'front') + ')';
        frontEl.style.backgroundSize = '100% 100%';
        frontEl.style.backgroundRepeat = 'no-repeat';
        frontEl.style.border = 'none';
      }
    }
    if ($('awFollowupBox')) $('awFollowupBox').classList.add('hidden');
    if ($('awProceedWrap')) $('awProceedWrap').classList.add('hidden');
    appState.awarenessFlipped = false;
  }"""

assert old_func_block in text, "old_func_block not found!"
text = text.replace(old_func_block, new_func_block, 1)

# 3. Update entryBtnCard total calculation
old_entry_btn = """      if (!appState.awarenessFlipped) {
        var total = (ZEN_CARDS_96 && ZEN_CARDS_96.length) ? ZEN_CARDS_96.length : (CARDS_MINDSET.length || 8);
        appState.awarenessIndex = Math.floor(Math.random() * total);
        renderAwarenessCard(appState.awarenessIndex);
      }"""

new_entry_btn = """      if (!appState.awarenessFlipped) {
        var total = (CARDS_MINDSET && CARDS_MINDSET.length) ? CARDS_MINDSET.length : 16;
        appState.awarenessIndex = Math.floor(Math.random() * total);
        renderAwarenessCard(appState.awarenessIndex);
      }"""

assert old_entry_btn in text, "old_entry_btn not found!"
text = text.replace(old_entry_btn, new_entry_btn, 1)

# 4. Update btnAwChange total calculation
old_change_btn = """      setTimeout(function() {
        var total = (ZEN_CARDS_96 && ZEN_CARDS_96.length) ? ZEN_CARDS_96.length : (CARDS_MINDSET.length || 8);
        var current = appState.awarenessIndex;
        var next = Math.floor(Math.random() * (total - 1));
        if (next >= current) next = (next + 1) % total;
        appState.awarenessIndex = next;
        renderAwarenessCard(appState.awarenessIndex);
        if (box) box.classList.add('is-flipped');
        appState.awarenessFlipped = true;
      }, 180);"""

new_change_btn = """      setTimeout(function() {
        var total = (CARDS_MINDSET && CARDS_MINDSET.length) ? CARDS_MINDSET.length : 16;
        var current = appState.awarenessIndex;
        var next = Math.floor(Math.random() * (total - 1));
        if (next >= current) next = (next + 1) % total;
        appState.awarenessIndex = next;
        renderAwarenessCard(appState.awarenessIndex);
        if (box) box.classList.add('is-flipped');
        appState.awarenessFlipped = true;
      }, 180);"""

assert old_change_btn in text, "old_change_btn not found!"
text = text.replace(old_change_btn, new_change_btn, 1)

# 5. Update bootstrap totalCards calculation
old_bootstrap = """    var totalCards = (ZEN_CARDS_96 && ZEN_CARDS_96.length) ? ZEN_CARDS_96.length : 8;
    appState.awarenessIndex = Math.floor(Math.random() * totalCards);
    renderAwarenessCard(appState.awarenessIndex);"""

new_bootstrap = """    var totalCards = (CARDS_MINDSET && CARDS_MINDSET.length) ? CARDS_MINDSET.length : 16;
    appState.awarenessIndex = Math.floor(Math.random() * totalCards);
    renderAwarenessCard(appState.awarenessIndex);"""

assert old_bootstrap in text, "old_bootstrap not found!"
text = text.replace(old_bootstrap, new_bootstrap, 1)

# 6. Update useZen96InRelief
old_use_zen = """  window.useZen96InRelief = function() {
    if (!currentZen96ModalCard) return;
    closeZen96Modal();
    switchTab('relief');
    var input = $('userInput');
    if (input) {
      input.value = '抽得觉察牌【' + currentZen96ModalCard.name + '】（核心寓意：' + currentZen96ModalCard.core + '）。想请先贤结合我的近况给予指引：\\n';
      input.focus();
    }
    showToast('已将【' + currentZen96ModalCard.name + '】带入解忧处，静候先贤批笺');
  };"""

new_use_zen = """  window.useZen96InRelief = function() {
    if (!currentZen96ModalCard) return;
    closeZen96Modal();
    if (typeof switchMainTab === 'function') switchMainTab('relief');
    if (typeof switchClientView === 'function') switchClientView('userHome');
    if ($('entryBtnDirect')) $('entryBtnDirect').click();
    var input = $('userTextarea') || $('userInput');
    if (input) {
      input.value = '抽得东方锦囊【' + currentZen96ModalCard.name + '】（核心智慧：“' + currentZen96ModalCard.core + '”）。想请先贤结合我的近况给予破局指引：\\n';
      input.dispatchEvent(new Event('input'));
      input.focus();
    }
    showToast('已将东方锦囊【' + currentZen96ModalCard.name + '】带入解忧处，静候先贤批笺');
  };
  window.switchTab = function(t) { if (typeof switchMainTab === 'function') switchMainTab(t); };"""

assert old_use_zen in text, "old_use_zen not found!"
text = text.replace(old_use_zen, new_use_zen, 1)

with open(template_path, "w", encoding="utf-8") as f:
    f.write(text)

print("[SUCCESS] _template.html successfully updated for Option A!")
