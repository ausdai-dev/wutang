# -*- coding: utf-8 -*-
"""
补丁脚本：将主理人工作台卡牌库改造为四大平级卡牌库体系
1. 基础解忧牌 (32)
2. 百八常道库 (108)
3. 觉察牌画廊 (96)
4. 主题卡牌包 (6)
四个卡牌库平级互斥切换，点击即开！
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

def main():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 结构化匹配 section id="studioCards"
    m_studio_cards = re.search(r'<section id="studioCards" class="card hidden">.*?<div class="studio-card-grid" id="studioCardListContainer"></div>\s*</section>', content, re.DOTALL)
    if not m_studio_cards:
        raise RuntimeError("m_studio_cards not found in _template.html")

    # 提取内部的三个卡牌库子视图
    m_p108 = re.search(r'(<div id="subViewPantheon108".*?</section>\s*</div>)', content, re.DOTALL)
    m_z96 = re.search(r'(<div id="subViewZen96".*?</section>\s*</div>)', content, re.DOTALL)
    m_theme = re.search(r'(<div id="subViewThemePacks".*?</section>\s*</div>)', content, re.DOTALL)

    if not (m_p108 and m_z96 and m_theme):
        print("m_p108:", bool(m_p108), "m_z96:", bool(m_z96), "m_theme:", bool(m_theme))
        raise RuntimeError("One or more subviews not matched!")

    p108_html = m_p108.group(1).strip()
    # 保证初始是隐藏的
    if 'style="display:none;"' not in p108_html[:80]:
        p108_html = p108_html.replace('class="card-library-subview"', 'class="card-library-subview" style="display:none;"', 1)

    z96_html = m_z96.group(1).strip()
    if 'style="display:none;"' not in z96_html[:80]:
        z96_html = z96_html.replace('class="card-library-subview"', 'class="card-library-subview" style="display:none;"', 1)

    theme_html = m_theme.group(1).strip()
    if 'style="display:none;"' not in theme_html[:80]:
        theme_html = theme_html.replace('class="card-library-subview"', 'class="card-library-subview" style="display:none;"', 1)

    # 构造全新的四大平级卡牌库 HTML
    new_studio_cards_html = f"""<section id="studioCards" class="card hidden">

        <!-- 顶部标题与说明 -->
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;flex-wrap:wrap;gap:12px;">

          <div>

            <h2 style="font-family:var(--font-serif);margin:0 0 6px;font-size:22px;" id="studioCardsMainTitle">东方解忧卡牌库 · 基础牌 (32张)</h2>

            <p style="margin:0;font-size:14px;color:var(--color-muted);" id="studioCardsSubtitle">

              收录心境牌 16、东方智慧牌 8（严格核验）与微行动牌 8 体系。

            </p>

          </div>

          <!-- 基础解忧卡牌类型下拉筛选器（仅在基础牌库激活时显示） -->
          <div id="studioCardTypeFilterWrap" style="display:flex;gap:8px;">

            <select class="form-select" id="studioCardTypeFilter" style="width:auto;padding:6px 12px;font-size:13.5px;">

              <option value="all">全部卡牌类型</option>

              <option value="mindset">心境牌（看见自己）</option>

              <option value="wisdom">东方智慧牌（换个视角 · 已核验）</option>

              <option value="action">行动牌（走出一步）</option>

            </select>

          </div>

        </div>



        <!-- 四大平级卡牌库导航选项卡 -->
        <div class="pill-inspirations" id="managerCardLifeTabs" style="margin:0 0 18px;display:flex;gap:8px;flex-wrap:wrap;">
          <button type="button" class="inspo-pill active" id="btnTabBase32" onclick="switchStudioCardLibrary('base32')">基础解忧牌 (32)</button>
          <button type="button" class="inspo-pill" id="btnTabPantheon" onclick="switchStudioCardLibrary('pantheon')">百八常道库 (108)</button>
          <button type="button" class="inspo-pill" id="btnTabZen96" onclick="switchStudioCardLibrary('zen96')">觉察牌画廊 (96)</button>
          <button type="button" class="inspo-pill" id="btnTabThemePacks" onclick="switchStudioCardLibrary('theme')">主题卡牌包 (6)</button>
        </div>



        <!-- 1. 基础解忧牌库 (32张) -->
        <div id="subViewBase32" class="card-library-subview">
          <div class="studio-card-grid" id="studioCardListContainer"></div>
        </div>



        <!-- 2. 百八常道 108 图鉴全谱系 (108张) -->
        {p108_html}



        <!-- 3. 东方智慧觉察牌 96 画廊 (96张) -->
        {z96_html}



        <!-- 4. 6 大主题卡牌包与详情 (6套) -->
        {theme_html}

      </section>"""

    content = content[:m_studio_cards.start()] + new_studio_cards_html + content[m_studio_cards.end():]

    # 2. 替换 JS 切换函数
    m_js = re.search(r'// ================= 主理人卡牌库：工作台内三类卡牌库切换 =================.*?window\.writeJournalWithFavCard = function', content, re.DOTALL)
    if not m_js:
        raise RuntimeError("m_js not found in _template.html")

    new_js = """// ================= 主理人卡牌库：四大平级卡牌库切换 (32基础 / 108常道 / 96觉察 / 6主题包) =================
  window.switchStudioCardLibrary = function(libKey) {
    libKey = libKey || 'base32';

    var tabsWrap = $('managerCardLifeTabs');
    var pills = tabsWrap ? tabsWrap.querySelectorAll('.inspo-pill') : [];
    Array.prototype.forEach.call(pills, function(p) { p.classList.remove('active'); });

    var btnMap = {
      base32: $('btnTabBase32'),
      pantheon: $('btnTabPantheon'),
      zen96: $('btnTabZen96'),
      theme: $('btnTabThemePacks')
    };
    if (btnMap[libKey]) btnMap[libKey].classList.add('active');

    var subBase = $('subViewBase32');
    var subPantheon = $('subViewPantheon108');
    var subZen96 = $('subViewZen96');
    var subTheme = $('subViewThemePacks');
    var filterWrap = $('studioCardTypeFilterWrap');

    if (subBase) subBase.style.display = (libKey === 'base32') ? 'block' : 'none';
    if (subPantheon) subPantheon.style.display = (libKey === 'pantheon') ? 'block' : 'none';
    if (subZen96) subZen96.style.display = (libKey === 'zen96') ? 'block' : 'none';
    if (subTheme) subTheme.style.display = (libKey === 'theme') ? 'block' : 'none';
    if (filterWrap) filterWrap.style.display = (libKey === 'base32') ? 'flex' : 'none';

    var mainTitle = $('studioCardsMainTitle');
    var subTitle = $('studioCardsSubtitle');

    if (libKey === 'base32') {
      if (mainTitle) mainTitle.textContent = '东方解忧卡牌库 · 基础牌 (32张)';
      if (subTitle) {
        var cM = (typeof CARDS_MINDSET !== 'undefined' && CARDS_MINDSET) ? CARDS_MINDSET.length : 16;
        var cW = (typeof CARDS_WISDOM !== 'undefined' && CARDS_WISDOM) ? CARDS_WISDOM.length : 8;
        var cA = (typeof CARDS_ACTION !== 'undefined' && CARDS_ACTION) ? CARDS_ACTION.length : 8;
        subTitle.textContent = '共 ' + (cM + cW + cA) + ' 张卡牌 · 心境 ' + cM + ' / 智慧 ' + cW + ' / 行动 ' + cA + '（收录心境牌、东方智慧牌与微行动牌体系）';
      }
      if (typeof renderStudioCards === 'function') {
        renderStudioCards($('studioCardTypeFilter') ? $('studioCardTypeFilter').value : 'all');
      }
    } else if (libKey === 'pantheon') {
      if (mainTitle) mainTitle.textContent = '儒释道卡牌人生 · 百八常道图鉴 (108张全谱系)';
      if (subTitle) subTitle.textContent = '立足东方智慧照亮人生之路。涵盖儒家修己（36鉴）、道家逍遥（36鉴）、释家觉照（36鉴），支持一键导出 300DPI 实体打印卡与 A4 拼版打印。';
      if (typeof renderPantheonSection === 'function') renderPantheonSection();
    } else if (libKey === 'zen96') {
      if (mainTitle) mainTitle.textContent = '悟堂 · 东方智慧觉察牌 (96张典藏画廊)';
      if (subTitle) subTitle.textContent = '848×1264 超清母版 · 以宋画留白、工笔设色与传统宣纸肌理绘制。包含禅心之境、一盏茶事、因缘相惜等六大系列。';
      if (typeof renderZen96CardsSection === 'function') renderZen96CardsSection();
    } else if (libKey === 'theme') {
      if (mainTitle) mainTitle.textContent = '东方解忧卡 · 主题卡牌包 (6大系列)';
      if (subTitle) subTitle.textContent = '按日常高频心境主题分类精选，点击浏览每个主题包的启发卡牌。';
      if (typeof renderThemePackGrid === 'function') renderThemePackGrid();
    }
  };

  // 兼容老函数名
  window.switchCardLifeSubView = function(subView) {
    window.switchStudioCardLibrary(subView);
  };

  window.writeJournalWithFavCard = function"""

    content = content[:m_js.start()] + new_js + content[m_js.end():]

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("[ok] Patched 4-in-1 equal card libraries successfully!")

if __name__ == "__main__":
    main()
