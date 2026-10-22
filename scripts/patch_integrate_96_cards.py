# -*- coding: utf-8 -*-
"""
无缝接入 96 张东方智慧觉察牌至 frontend/_template.html，
并运行 build_frontend.py 重新生成生产级 frontend/index.html。
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# 1. 注入 ZEN_CARDS_96 数据变量定义
target_var = "var PRACTICE_SCENARIOS = RAW_DATA.practiceScenarios || [];"
repl_var = """var PRACTICE_SCENARIOS = RAW_DATA.practiceScenarios || [];
  var ZEN_CARDS_96 = RAW_DATA.zenCards96 || [];"""

if target_var in html and "var ZEN_CARDS_96" not in html:
    html = html.replace(target_var, repl_var, 1)
    print("[ok] Injected var ZEN_CARDS_96")

# 2. 在 cardsArea 中插入 96 张卡牌典藏画廊与随机抽卡专区
target_cards_area = '<main id="cardsArea" class="hidden">\n    <div style="display:flex;flex-direction:column;gap:18px;">'
repl_cards_area = """<main id="cardsArea" class="hidden">
    <div style="display:flex;flex-direction:column;gap:18px;">

      <!-- 悟堂 · 东方智慧觉察牌 (96张典藏) 专区 (PRD 3.0 / 848x1264) -->
      <section class="card" id="zen96CardsSection">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:14px;">
          <div>
            <span class="badge ok" style="margin-bottom:6px;">848×1264 超清母版 · 宋画工笔纸本</span>
            <h2 style="font-family:var(--font-serif);margin:0 0 6px;font-size:24px;">悟堂 · 东方智慧觉察牌（96张典藏画廊）</h2>
            <p style="margin:0;font-size:13.5px;color:var(--color-muted);">
              以宋画留白、工笔设色与传统宣纸肌理独立绘制。包含禅心之境、一盏茶事、因缘相惜、道法自然、君子修身、山水人生六大系列。
            </p>
          </div>
          <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
            <button class="btn sm" id="btnZen96DrawRandom" onclick="drawRandomZen96Card()">随机抽取觉察牌 ✨</button>
            <a href="zen_cards_app.html" target="_blank" class="btn sm secondary" style="text-decoration:none;display:inline-flex;align-items:center;">独立 3D 抽卡体验端 ↗</a>
          </div>
        </div>

        <!-- 六大系列快速分类按钮 -->
        <div class="pill-inspirations" id="zen96FilterBar" style="margin-bottom:18px;display:flex;flex-wrap:wrap;gap:8px;">
          <button class="inspo-pill active" onclick="filterZen96Cards('全部', this)">全部 (96)</button>
          <button class="inspo-pill" onclick="filterZen96Cards('禅心之境', this)">禅心之境 (16)</button>
          <button class="inspo-pill" onclick="filterZen96Cards('一盏茶事', this)">一盏茶事 (16)</button>
          <button class="inspo-pill" onclick="filterZen96Cards('因缘相惜', this)">因缘相惜 (16)</button>
          <button class="inspo-pill" onclick="filterZen96Cards('道法自然', this)">道法自然 (16)</button>
          <button class="inspo-pill" onclick="filterZen96Cards('君子修身', this)">君子修身 (16)</button>
          <button class="inspo-pill" onclick="filterZen96Cards('山水人生', this)">山水人生 (16)</button>
        </div>

        <!-- 96 张卡牌画廊展示网格 -->
        <div class="studio-card-grid" id="zen96CardsGrid" style="grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 18px;"></div>
      </section>"""

if target_cards_area in html and 'id="zen96CardsSection"' not in html:
    html = html.replace(target_cards_area, repl_cards_area, 1)
    print("[ok] Injected zen96CardsSection in cardsArea")

# 3. 注入 3D 卡牌详情赏析弹窗
target_body_end = "</body>"
modal_html = """
  <!-- ================= 96 张东方觉察牌 3D 沉浸式大图弹窗 ================= -->
  <div id="zen96Modal" class="modal-overlay hidden" style="z-index:9999;display:flex;align-items:center;justify-content:center;">
    <div class="modal-card" style="max-width:540px;width:92%;background:#FAF6EF;border:1px solid #D9CEBD;border-radius:12px;padding:26px 22px;position:relative;box-shadow:0 24px 60px rgba(0,0,0,0.22);max-height:92vh;overflow-y:auto;">
      <button style="position:absolute;top:14px;right:16px;background:none;border:none;font-size:22px;cursor:pointer;color:#7A736C;" onclick="closeZen96Modal()">✕</button>
      
      <div style="text-align:center;margin-bottom:14px;">
        <span class="badge ok" id="zen96ModalSeriesBadge" style="margin-bottom:6px;">禅心之境 · 01</span>
        <h3 id="zen96ModalTitle" style="font-family:var(--font-serif);margin:4px 0 8px;font-size:22px;color:var(--color-ink);">静观</h3>
        <p id="zen96ModalCore" style="margin:0 0 12px;font-size:15px;color:var(--color-primary);font-family:var(--font-serif);line-height:1.6;"></p>
      </div>

      <!-- 3D 翻转卡牌舞台 -->
      <div style="perspective:1000px;width:280px;height:418px;margin:0 auto 18px;cursor:pointer;" onclick="toggleZen96ModalFlip()" title="点击翻转卡牌查看正反面">
        <div id="zen96ModalFlipper" style="width:100%;height:100%;position:relative;transform-style:preserve-3d;transition:transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);border-radius:10px;box-shadow:0 12px 28px rgba(44,40,37,0.18);">
          <!-- 正面 (超清水墨原图) -->
          <div style="position:absolute;width:100%;height:100%;backface-visibility:hidden;border-radius:10px;overflow:hidden;border:1px solid #D9CEBD;background:#EAE4D8;">
            <img id="zen96ModalImg" src="" alt="" style="width:100%;height:100%;object-fit:cover;">
          </div>
          <!-- 反面 (自省引导与解忧问句) -->
          <div style="position:absolute;width:100%;height:100%;backface-visibility:hidden;transform:rotateY(180deg);background:#FCF9F2;border-radius:10px;border:2px solid #D9CEBD;padding:26px 20px;display:flex;flex-direction:column;justify-content:space-between;text-align:left;box-sizing:border-box;">
            <div>
              <div style="font-size:12px;color:#7A736C;letter-spacing:0.12em;margin-bottom:6px;" id="zen96ModalBackNum">悟堂 · 东方觉察牌</div>
              <h4 style="font-family:var(--font-serif);margin:0 0 12px;font-size:20px;" id="zen96ModalBackTitle">静观</h4>
              <div style="width:36px;height:2px;background:#B89658;margin-bottom:14px;"></div>
              <p style="font-size:13.5px;color:#4A443E;line-height:1.75;margin:0 0 16px;" id="zen96ModalBackScene"></p>
            </div>
            <div>
              <div style="background:#F2ECE1;border-left:3px solid #B89658;padding:12px 14px;border-radius:4px;font-size:13px;line-height:1.65;color:#2C2825;margin-bottom:10px;" id="zen96ModalBackQuestion"></div>
              <div style="font-size:11px;color:#8E867E;text-align:center;">轻触任意处可翻回正面画作</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作与跳转 -->
      <div style="display:flex;flex-direction:column;gap:10px;">
        <div style="display:flex;gap:10px;justify-content:center;">
          <button class="btn sm" id="btnZen96UseInRelief" onclick="useZen96InRelief()">以这张牌开启今日解忧 →</button>
          <button class="btn sm secondary" id="btnZen96FavToggle" onclick="toggleZen96ModalFav()">☆ 珍藏此卡</button>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:0 8px;">
          <button class="btn ghost sm" onclick="prevZen96Card()">← 上一张</button>
          <span style="font-size:12px;color:var(--color-muted);" id="zen96ModalCounter">1 / 96</span>
          <button class="btn ghost sm" onclick="nextZen96Card()">下一张 →</button>
        </div>
      </div>
    </div>
  </div>
""" + target_body_end

if target_body_end in html and 'id="zen96Modal"' not in html:
    html = html.replace(target_body_end, modal_html, 1)
    print("[ok] Injected zen96Modal")

# 4. 注入 JavaScript 逻辑：画廊渲染、3D翻转、收藏联动与解忧打通
js_logic = """
  // ==========================================================================
  // 96 张东方觉察牌（848x1264）画廊、抽卡与解忧融合引擎
  // ==========================================================================
  var currentZen96Filter = '全部';
  var currentZen96ModalCard = null;

  function renderZen96CardsSection() {
    var grid = $('zen96CardsGrid');
    if (!grid) return;
    if (!ZEN_CARDS_96 || !ZEN_CARDS_96.length) {
      grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--color-muted);">卡牌资产正在加载...</div>';
      return;
    }

    var list = (currentZen96Filter === '全部') 
      ? ZEN_CARDS_96 
      : ZEN_CARDS_96.filter(function(c) { return c.series === currentZen96Filter; });

    var favList = getStorageJson('wutang_favorite_cards', []);

    grid.innerHTML = list.map(function(c) {
      var isFav = (favList.indexOf(c.card_id) !== -1);
      return '<div class="studio-card-item" style="padding:0;overflow:hidden;border:1px solid #D9CEBD;background:#FAF6EF;display:flex;flex-direction:column;">'
        + '  <div style="width:100%;aspect-ratio:2/3;background:#E8E2D6;overflow:hidden;cursor:pointer;position:relative;" onclick="openZen96CardModal(\\'' + c.card_id + '\\')">'
        + '    <img src="' + c.image_png + '" alt="' + esc(c.name) + '" loading="lazy" style="width:100%;height:100%;object-fit:cover;transition:transform 0.3s ease;">'
        + '    <div style="position:absolute;bottom:8px;right:8px;background:rgba(42,38,35,0.75);color:#fff;font-size:11px;padding:2px 8px;border-radius:12px;backdrop-filter:blur(4px);">3D 赏析</div>'
        + '  </div>'
        + '  <div style="padding:12px 14px;flex:1;display:flex;flex-direction:column;justify-content:space-between;">'
        + '    <div>'
        + '      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
        + '        <span class="badge ok" style="font-size:11px;padding:1px 6px;">' + esc(c.series) + ' · ' + c.num + '</span>'
        + '        <button class="btn ghost sm" style="padding:2px 6px;font-size:12px;" onclick="toggleFavoriteCard(\\'' + c.card_id + '\\')">'
        + (isFav ? '★' : '☆')
        + '        </button>'
        + '      </div>'
        + '      <h4 style="font-family:var(--font-serif);margin:4px 0 6px;font-size:17px;font-weight:bold;">' + esc(c.name) + '</h4>'
        + '      <p style="margin:0 0 8px;font-size:12.5px;color:var(--color-primary);font-family:var(--font-serif);line-height:1.5;">“' + esc(c.core) + '”</p>'
        + '    </div>'
        + '    <button class="btn sm secondary" style="width:100%;margin-top:6px;font-size:12.5px;padding:6px 0;" onclick="openZen96CardModal(\\'' + c.card_id + '\\')">翻看自省导语</button>'
        + '  </div>'
        + '</div>';
    }).join('');
  }

  window.filterZen96Cards = function(series, btnEl) {
    currentZen96Filter = series;
    var container = $('zen96FilterBar');
    if (container) {
      var btns = container.querySelectorAll('.inspo-pill');
      btns.forEach(function(b) { b.classList.remove('active'); });
      if (btnEl) btnEl.classList.add('active');
    }
    renderZen96CardsSection();
  };

  window.openZen96CardModal = function(cardId) {
    if (!ZEN_CARDS_96 || !ZEN_CARDS_96.length) return;
    var card = ZEN_CARDS_96.find(function(item) { return item.card_id === cardId; });
    if (!card) card = ZEN_CARDS_96[0];
    currentZen96ModalCard = card;

    if ($('zen96ModalSeriesBadge')) $('zen96ModalSeriesBadge').textContent = card.series + ' · ' + card.num;
    if ($('zen96ModalTitle')) $('zen96ModalTitle').textContent = card.name;
    if ($('zen96ModalCore')) $('zen96ModalCore').textContent = '“' + card.core + '”';
    if ($('zen96ModalImg')) $('zen96ModalImg').src = card.image_png;

    if ($('zen96ModalBackTitle')) $('zen96ModalBackTitle').textContent = card.name;
    if ($('zen96ModalBackNum')) $('zen96ModalBackNum').textContent = '【' + card.series + ' · 编号 ' + card.num + '】';
    if ($('zen96ModalBackScene')) $('zen96ModalBackScene').textContent = '画面意境：' + (card.scene || card.core);
    if ($('zen96ModalBackQuestion')) $('zen96ModalBackQuestion').textContent = '💡 觉察问句：' + (card.question || '静观当下，细细觉察此刻的真实发生。');

    var idx = ZEN_CARDS_96.indexOf(card);
    if ($('zen96ModalCounter')) $('zen96ModalCounter').textContent = (idx + 1) + ' / ' + ZEN_CARDS_96.length;

    var favList = getStorageJson('wutang_favorite_cards', []);
    var isFav = (favList.indexOf(card.card_id) !== -1);
    if ($('btnZen96FavToggle')) $('btnZen96FavToggle').textContent = isFav ? '★ 已珍藏' : '☆ 珍藏此卡';

    var flipper = $('zen96ModalFlipper');
    if (flipper) flipper.style.transform = 'rotateY(0deg)';

    var modal = $('zen96Modal');
    if (modal) modal.classList.remove('hidden');
  };

  window.closeZen96Modal = function() {
    var modal = $('zen96Modal');
    if (modal) modal.classList.add('hidden');
  };

  window.toggleZen96ModalFlip = function() {
    var flipper = $('zen96ModalFlipper');
    if (!flipper) return;
    var isFlipped = (flipper.style.transform === 'rotateY(180deg)');
    flipper.style.transform = isFlipped ? 'rotateY(0deg)' : 'rotateY(180deg)';
  };

  window.prevZen96Card = function() {
    if (!currentZen96ModalCard || !ZEN_CARDS_96.length) return;
    var idx = ZEN_CARDS_96.indexOf(currentZen96ModalCard);
    var prevIdx = (idx - 1 + ZEN_CARDS_96.length) % ZEN_CARDS_96.length;
    openZen96CardModal(ZEN_CARDS_96[prevIdx].card_id);
  };

  window.nextZen96Card = function() {
    if (!currentZen96ModalCard || !ZEN_CARDS_96.length) return;
    var idx = ZEN_CARDS_96.indexOf(currentZen96ModalCard);
    var nextIdx = (idx + 1) % ZEN_CARDS_96.length;
    openZen96CardModal(ZEN_CARDS_96[nextIdx].card_id);
  };

  window.drawRandomZen96Card = function() {
    if (!ZEN_CARDS_96 || !ZEN_CARDS_96.length) return;
    var rnd = Math.floor(Math.random() * ZEN_CARDS_96.length);
    openZen96CardModal(ZEN_CARDS_96[rnd].card_id);
  };

  window.toggleZen96ModalFav = function() {
    if (!currentZen96ModalCard) return;
    toggleFavoriteCard(currentZen96ModalCard.card_id);
    var favList = getStorageJson('wutang_favorite_cards', []);
    var isFav = (favList.indexOf(currentZen96ModalCard.card_id) !== -1);
    if ($('btnZen96FavToggle')) $('btnZen96FavToggle').textContent = isFav ? '★ 已珍藏' : '☆ 珍藏此卡';
    renderZen96CardsSection();
  };

  window.useZen96InRelief = function() {
    if (!currentZen96ModalCard) return;
    closeZen96Modal();
    switchTab('relief');
    var input = $('userInput');
    if (input) {
      input.value = '抽得觉察牌【' + currentZen96ModalCard.name + '】（核心寓意：' + currentZen96ModalCard.core + '）。想请先贤结合我的近况给予指引：\\n';
      input.focus();
    }
    showToast('已将【' + currentZen96ModalCard.name + '】带入解忧处，静候先贤批笺');
  };
"""

target_render_cards = "function renderCardsSection() {\n    renderThemePackGrid();\n    renderFavoriteCards();\n  }"
repl_render_cards = """function renderCardsSection() {
    renderZen96CardsSection();
    renderThemePackGrid();
    renderFavoriteCards();
  }
""" + js_logic

if target_render_cards in html and "renderZen96CardsSection()" not in html:
    html = html.replace(target_render_cards, repl_render_cards, 1)
    print("[ok] Injected renderZen96CardsSection into renderCardsSection")

# 5. 升级首页翻一张觉察牌 (renderAwarenessCard)，优先采用 96 张超清水墨工笔画作
target_aw = """  function renderAwarenessCard(idx) {
    if (!CARDS_MINDSET.length) return;
    var i = Math.abs(idx) % CARDS_MINDSET.length;
    var card = CARDS_MINDSET[i];"""

repl_aw = """  function renderAwarenessCard(idx) {
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
    var card = CARDS_MINDSET[i];"""

if target_aw in html:
    html = html.replace(target_aw, repl_aw, 1)
    print("[ok] Upgraded renderAwarenessCard with ZEN_CARDS_96")

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("[ok] Saved updated frontend/_template.html")
