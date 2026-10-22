# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = "frontend/_template.html"
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 注入 108 卡牌人生图鉴区域
PANTHEON_HTML = """      <!-- PRD 4.0 儒释道卡牌人生 · 百八常道图鉴 (108张全谱系) -->
      <section class="card" id="pantheon108Section" style="border:1.5px solid var(--color-gold-border);background:var(--color-surface);">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:14px;">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <span class="badge" style="background:#8E2927;color:#FFF;">儒释道三学</span>
              <span class="badge ok">108 百八常道卡牌人生</span>
              <span class="badge" style="background:var(--color-gold-bg);color:var(--color-gold);border:1px solid var(--color-gold-border);">300 DPI 工业实体打印级</span>
            </div>
            <h2 style="font-family:var(--font-serif);margin:0 0 6px;font-size:24px;color:var(--color-ink);">儒释道卡牌人生 · 百八常道图鉴（108张）</h2>
            <p style="margin:0;font-size:13.5px;color:var(--color-muted);">
              立足东方智慧照亮人生之路。涵盖儒家修己（36鉴）、道家逍遥（36鉴）、释家觉照（36鉴）。支持一键导出 300DPI 实体打印卡与 A4 9宫格拼版打印。
            </p>
          </div>
          <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
            <button class="btn sm" id="btnPreviewA4Print" onclick="toggleA4PrintModal(true)">🖨️ A4 拼版打印预览 (一页9张)</button>
            <button class="btn sm secondary" onclick="drawRandomPantheonCard()">随机参悟一鉴 ✨</button>
          </div>
        </div>

        <!-- 流派筛选 -->
        <div class="pill-inspirations" id="pantheonFilterBar" style="margin-bottom:16px;display:flex;flex-wrap:wrap;gap:8px;">
          <button class="inspo-pill active" onclick="filterPantheonCards('all', this)">全部常道 (108)</button>
          <button class="inspo-pill" onclick="filterPantheonCards('confucianism', this)">儒学 · 君子修己 (36)</button>
          <button class="inspo-pill" onclick="filterPantheonCards('daoism', this)">道学 · 顺应逍遥 (36)</button>
          <button class="inspo-pill" onclick="filterPantheonCards('buddhism', this)">释学 · 破执觉照 (36)</button>
        </div>

        <!-- 108 卡牌展示网格 -->
        <div id="pantheonCardsGrid" style="display:grid;grid-template-columns:repeat(auto-fill, minmax(180px, 1fr));gap:14px;max-height:680px;overflow-y:auto;padding-right:6px;"></div>
      </section>

      <!-- A4 拼版打印弹窗模态框 -->
      <div id="modalA4Print" class="modal-overlay hidden" style="position:fixed;inset:0;background:rgba(0,0,0,0.65);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px;">
        <div style="background:#FFF;width:100%;max-width:920px;max-height:90vh;border-radius:16px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 50px rgba(0,0,0,0.3);">
          <div style="padding:16px 20px;border-bottom:1px solid var(--color-border);display:flex;justify-content:space-between;align-items:center;">
            <h3 style="font-family:var(--font-serif);margin:0;font-size:18px;">A4 实体卡牌 9宫格拼版打印预览（3x3 布局，带裁切基准线）</h3>
            <button class="btn sm secondary" onclick="toggleA4PrintModal(false)">✕ 关闭</button>
          </div>
          <div style="padding:20px;overflow-y:auto;background:#F5F2EB;text-align:center;">
            <p style="font-size:12.5px;color:var(--color-muted);margin:0 0 14px;">
              标准 A4 纸张（210mm x 297mm），单页完美容纳 9 张 TCG 规格卡牌（63mm x 88mm）。使用彩色打印机直接打印，沿虚线剪裁即可装入实体集卡册！
            </p>
            <div id="a4PrintSheet" style="width:100%;max-width:700px;margin:0 auto;background:#FFF;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,0.15);display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;border:1px dashed #CCC;">
              <!-- 动态填入9张卡 -->
            </div>
          </div>
          <div style="padding:14px 20px;border-top:1px solid var(--color-border);display:flex;justify-content:flex-end;gap:10px;background:#FAF8F3;">
            <button class="btn sm secondary" onclick="toggleA4PrintModal(false)">取消</button>
            <button class="btn sm primary" onclick="window.print()">🖨️ 调用系统打印机立即打印 (Ctrl+P)</button>
          </div>
        </div>
      </div>
"""

TARGET_CARDS_START = '<!-- 悟堂 · 东方智慧觉察牌 (96张典藏) 专区'
if "id=\"pantheon108Section\"" not in content and TARGET_CARDS_START in content:
    content = content.replace(TARGET_CARDS_START, PANTHEON_HTML + "\n\n      " + TARGET_CARDS_START, 1)
    print("[ok] Injected 108 Pantheon section HTML into cardsArea")

# 2. 注入 108 卡牌渲染 JS 逻辑
JS_PANTHEON = """
  // ==========================================================================
  // 108 百八常道卡牌人生图鉴与 A4 拼版打印引擎
  // ==========================================================================
  var currentPantheonFilter = 'all';

  function renderPantheonSection() {
    var grid = $('pantheonCardsGrid');
    if (!grid) return;
    var cards = (window.__WUTANG_DATA__ && window.__WUTANG_DATA__.zenCards108) ? window.__WUTANG_DATA__.zenCards108 : [];
    if (!cards.length) {
      grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--color-muted);">卡牌图鉴资产正在加载中...</div>';
      return;
    }

    var list = (currentPantheonFilter === 'all')
      ? cards
      : cards.filter(function(c) { return c.school === currentPantheonFilter; });

    grid.innerHTML = list.map(function(c) {
      var schColor = (c.school === 'daoism') ? '#2B4C5F' : ((c.school === 'buddhism') ? '#B58900' : '#8E2927');
      var schName = (c.school === 'daoism') ? '道学·老子' : ((c.school === 'buddhism') ? '释学·佛陀' : '儒学·孔子');

      return '<div style="background:#FFF;border:1px solid var(--color-border);border-radius:10px;padding:12px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 2px 6px rgba(0,0,0,0.02);transition:all 0.2s;" onmouseover="this.style.transform=\\'translateY(-2px)\\'" onmouseout="this.style.transform=\\'none\\'">'
        + '<div>'
        + '  <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--color-muted);margin-bottom:6px;">'
        + '    <span style="color:' + schColor + ';font-weight:700;">' + esc(schName) + '</span>'
        + '    <span>' + esc(c.num) + '</span>'
        + '  </div>'
        + '  <div style="font-family:var(--font-serif);font-size:20px;font-weight:700;color:' + schColor + ';margin-bottom:4px;">【 ' + esc(c.name) + ' 】</div>'
        + '  <div style="font-size:11.5px;color:var(--color-gold);font-family:var(--font-serif);margin-bottom:6px;">' + esc(c.master_motto || '') + '</div>'
        + '  <div style="font-size:12px;color:var(--color-ink-light);line-height:1.5;margin-bottom:8px;">' + esc(c.core) + '</div>'
        + '</div>'
        + '<div style="border-top:1px dashed var(--color-border);padding-top:8px;display:flex;justify-content:space-between;align-items:center;font-size:11px;">'
        + '  <span style="color:var(--color-muted);">' + esc(c.series) + '</span>'
        + '  <button class="btn sm" style="padding:2px 8px;font-size:11px;" onclick="selectPantheonCardToConsult(\\'' + esc(c.name) + '\\', \\'' + esc(c.school) + '\\')">由此开悟</button>'
        + '</div>'
        + '</div>';
    }).join('');
  }

  function filterPantheonCards(sch, btn) {
    currentPantheonFilter = sch;
    var bar = $('pantheonFilterBar');
    if (bar) {
      var pills = bar.querySelectorAll('.inspo-pill');
      pills.forEach(function(p) { p.classList.remove('active'); });
      if (btn) btn.classList.add('active');
    }
    renderPantheonSection();
  }

  function toggleA4PrintModal(show) {
    var modal = $('modalA4Print');
    if (!modal) return;
    if (show) {
      modal.classList.remove('hidden');
      renderA4SheetCards();
    } else {
      modal.classList.add('hidden');
    }
  }

  function renderA4SheetCards() {
    var sheet = $('a4PrintSheet');
    if (!sheet) return;
    var cards = (window.__WUTANG_DATA__ && window.__WUTANG_DATA__.zenCards108) ? window.__WUTANG_DATA__.zenCards108 : [];
    // 默认选取前9张不同门类的代表卡
    var sample9 = cards.slice(0, 9);
    sheet.innerHTML = sample9.map(function(c) {
      var schColor = (c.school === 'daoism') ? '#2B4C5F' : ((c.school === 'buddhism') ? '#B58900' : '#8E2927');
      return '<div style="border:1.5px solid ' + schColor + ';border-radius:8px;padding:10px;text-align:center;background:#FAF8F2;aspect-ratio:2.5/3.5;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;">'
        + '<div style="font-size:10px;color:var(--color-muted);display:flex;justify-content:space-between;"><span>悟堂·常道</span><span>' + esc(c.num) + '</span></div>'
        + '<div><div style="font-family:var(--font-serif);font-size:24px;font-weight:700;color:' + schColor + ';">【 ' + esc(c.name) + ' 】</div>'
        + '<div style="font-size:11px;color:' + schColor + ';margin-top:2px;">' + esc(c.master) + '</div></div>'
        + '<div style="font-size:10.5px;color:var(--color-ink-light);line-height:1.4;">' + esc(c.core.slice(0, 24)) + '</div>'
        + '<div style="border-top:1px dashed #CCC;padding-top:4px;font-size:9.5px;color:var(--color-muted);">300 DPI 裁切线 63x88mm</div>'
        + '</div>';
    }).join('');
  }

  function selectPantheonCardToConsult(cardName, school) {
    if ($('userTextarea')) {
      $('userTextarea').value = '先圣在上，弟子在【' + cardName + '】一关偶有困惑，求宗师指点迷津...';
      $('userTextarea').dispatchEvent(new Event('input'));
    }
    // 切换到对应流派
    if ($('schoolTrackPills')) {
      var pills = $('schoolTrackPills').querySelectorAll('.school-pill');
      pills.forEach(function(p) {
        if (p.getAttribute('data-track') === school) {
          p.click();
        }
      });
    }
    switchMainTab('relief');
    if ($('userTextarea')) $('userTextarea').focus();
    showToast('已选定【' + cardName + '】心结，正在为您引导至解忧道席');
  }

  function drawRandomPantheonCard() {
    var cards = (window.__WUTANG_DATA__ && window.__WUTANG_DATA__.zenCards108) ? window.__WUTANG_DATA__.zenCards108 : [];
    if (!cards.length) return;
    var idx = Math.floor(Math.random() * cards.length);
    var c = cards[idx];
    selectPantheonCardToConsult(c.name, c.school);
  }
"""

if "renderPantheonSection" not in content:
    content = content.replace("function renderCardsSection() {", JS_PANTHEON + "\n\n  function renderCardsSection() {\n    renderPantheonSection();", 1)
    print("[ok] Injected renderPantheonSection into renderCardsSection")

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"[success] Updated {TEMPLATE_PATH}! Size: {len(content)} bytes")
