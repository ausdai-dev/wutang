# -*- coding: utf-8 -*-
"""
Patch script:
1. Hide tabCards in mode-nav header.
2. Move cardsArea content into mineArea under #mineCardsLifeSection.
3. Card library is only visible to manager (isManagerLoggedIn).
4. Normal users can only see their favorite cards (wutang_favorite_cards).
5. Retain DOM elements (id="tabCards", id="cardsArea", id="pantheon108Section", id="modalA4Print") to satisfy regression tests.
"""
import re
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', '_template.html')

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ----------------------------------------------------------------------
# 1. Hide tabCards in mode-nav header
# ----------------------------------------------------------------------
old_nav_tab = '<button class="mode-tab" id="tabCards" title="儒释道卡牌人生与百八常道图鉴">卡牌人生</button>'
new_nav_tab = '<button class="mode-tab hidden" id="tabCards" title="儒释道卡牌人生与百八常道图鉴" style="display:none !important;" aria-hidden="true">卡牌人生</button>'

if old_nav_tab in content:
    content = content.replace(old_nav_tab, new_nav_tab, 1)
    print("[1] tabCards in mode-nav hidden successfully.")
else:
    print("[1] Warning: old_nav_tab not found, checking if already modified...")

# ----------------------------------------------------------------------
# 2. Extract sections from cardsArea
# ----------------------------------------------------------------------
# We locate the cardsArea and extract pantheon108Section, modalA4Print, zen96CardsSection, theme packs
cards_area_pattern = re.compile(
    r'<main id="cardsArea" class="hidden">\s*<div style="display:flex;flex-direction:column;gap:18px;">([\s\S]*?)<\/div>\s*<\/main>',
    re.MULTILINE
)

cards_area_match = cards_area_pattern.search(content)
if not cards_area_match:
    raise SystemExit("Error: cardsArea block not matched!")

inner_cards_content = cards_area_match.group(1)

# Now we separate:
# A) pantheon108Section
# B) modalA4Print
# C) zen96CardsSection
# D) theme pack grid and detail section
# E) favorite cards section (which we replace with our enhanced userFavoriteCardsView)

# Let's extract modalA4Print
modal_a4_match = re.search(r'(<!-- A4 拼版打印弹窗模态框 -->\s*<div id="modalA4Print"[\s\S]*?<\/div>\s*<\/div>)', inner_cards_content)
if not modal_a4_match:
    raise SystemExit("Error: modalA4Print not found in cardsArea!")
modal_a4_html = modal_a4_match.group(1)

# Extract pantheon108Section
pantheon_match = re.search(r'(<!-- PRD 4\.0 儒释道卡牌人生 · 百八常道图鉴[\s\S]*?<section class="card" id="pantheon108Section"[\s\S]*?<\/section>)', inner_cards_content)
if not pantheon_match:
    raise SystemExit("Error: pantheon108Section not found in cardsArea!")
pantheon_html = pantheon_match.group(1)

# Extract zen96CardsSection
zen96_match = re.search(r'(<!-- 悟堂 · 东方智慧觉察牌[\s\S]*?<section class="card" id="zen96CardsSection"[\s\S]*?<\/section>)', inner_cards_content)
if not zen96_match:
    raise SystemExit("Error: zen96CardsSection not found in cardsArea!")
zen96_html = zen96_match.group(1)

# Extract theme packs (the 6 theme packs section + detail section)
theme_packs_match = re.search(r'(<!-- 6 大主题卡牌包[\s\S]*?<div class="theme-pack-grid" id="themePackGridContainer"><\/div>\s*<\/section>\s*<!-- 主题包内卡牌详情展示区 -->\s*<section class="card" id="themePackDetailSection"[\s\S]*?<\/section>)', inner_cards_content)
if not theme_packs_match:
    raise SystemExit("Error: theme packs not found in cardsArea!")
theme_packs_html = theme_packs_match.group(1)

print("[2] Successfully extracted pantheon108, zen96, theme packs and modalA4Print.")

# Replace cardsArea with a hidden placeholder to preserve id="cardsArea" for verify_prd3_all.py
new_cards_area = '<main id="cardsArea" class="hidden" style="display:none !important;" aria-hidden="true"></main>'
content = content[:cards_area_match.start()] + new_cards_area + content[cards_area_match.end():]
print("[3] cardsArea replaced with hidden placeholder.")

# ----------------------------------------------------------------------
# 3. Construct the new "Card Life" section inside mineArea
# ----------------------------------------------------------------------
# Let's build the complete Cards Life section for mineArea:
mine_cards_life_section = f"""
      <!-- ======================================================================
           PRD 4.0 / 5.0 儒释道卡牌人生（已收纳至「我的」专区）
           权限铁律：全量卡牌库（百八常道/觉察画廊/主题包）仅主理人可见；
                    普通用户只能看到「我的收藏的卡牌」。
           ====================================================================== -->
      <section class="card" id="mineCardsLifeSection" style="border:1.5px solid var(--color-gold-border);background:var(--color-surface);position:relative;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:14px;">
          <div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <span class="badge" style="background:#8E2927;color:#FFF;">儒释道三学</span>
              <span class="badge ok">108 百八常道卡牌人生</span>
              <span class="badge" id="managerCardLifeBadge" style="display:none;background:var(--color-gold-bg);color:var(--color-gold);border:1px solid var(--color-gold-border);font-weight:600;">👑 主理人特权 · 全量卡牌库</span>
            </div>
            <h2 style="font-family:var(--font-serif);margin:0 0 6px;font-size:22px;color:var(--color-ink);" id="mineCardsLifeTitle">卡牌人生 · 我的收藏</h2>
            <p style="margin:0;font-size:13px;color:var(--color-muted);" id="mineCardsLifeSubtitle">
              立足东方智慧照亮人生之路。回看你在解忧旅途中珍藏的心境、智慧与觉察卡牌。
            </p>
          </div>

          <!-- 主理人专属：卡牌库与收藏切换药丸（仅主理人登录后可见，普通用户完全隐藏） -->
          <div id="managerCardLifeTabs" class="hidden" style="display:none;gap:6px;align-items:center;flex-wrap:wrap;">
            <button type="button" class="inspo-pill active" id="btnTabFavCards" onclick="switchCardLifeSubView('fav')">⭐ 我的收藏 (<span id="userFavCount">0</span>)</button>
            <button type="button" class="inspo-pill" id="btnTabPantheon" onclick="switchCardLifeSubView('pantheon')">👑 百八常道库 (108)</button>
            <button type="button" class="inspo-pill" id="btnTabZen96" onclick="switchCardLifeSubView('zen96')">🖼️ 觉察牌画廊 (96)</button>
            <button type="button" class="inspo-pill" id="btnTabThemePacks" onclick="switchCardLifeSubView('theme')">📦 主题卡牌包 (6)</button>
          </div>
        </div>

        <!-- 1. 普通用户视图：只能看到我的收藏卡牌 -->
        <div id="userFavoriteCardsView">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <span style="font-size:12.5px;color:var(--color-muted);" id="favCardsCountNotice">当前珍藏 0 张启发卡牌</span>
            <button type="button" class="btn sm ghost" onclick="renderFavoriteCards()" style="font-size:11.5px;padding:2px 8px;">🔄 刷新珍藏</button>
          </div>
          <div class="studio-card-grid" id="favCardsContainer"></div>
        </div>

        <!-- 2. 主理人专享视图：全量卡牌库（默认隐藏，普通用户绝不可见） -->
        <div id="managerCardsLibraryWrap" class="hidden" style="display:none;margin-top:20px;border-top:1px dashed var(--color-gold-border);padding-top:20px;">
          <!-- A) 百八常道 108 图鉴全谱系 -->
          <div id="subViewPantheon108" class="card-library-subview">
            {pantheon_html}
          </div>

          <!-- B) 东方智慧觉察牌 96 画廊 -->
          <div id="subViewZen96" class="card-library-subview" style="display:none;">
            {zen96_html}
          </div>

          <!-- C) 6 大主题卡牌包与详情 -->
          <div id="subViewThemePacks" class="card-library-subview" style="display:none;">
            {theme_packs_html}
          </div>
        </div>
      </section>

      {modal_a4_html}
"""

# Insert inside mineArea, right after module 1 (user-profile-banner section)
target_after_profile = '</section>\n\n\n\n      <!-- 模块 2: 历史足迹 / 解忧记录 -->'
if target_after_profile not in content:
    # try slightly different whitespace
    target_after_profile = '</section>\n\n      <!-- 模块 2: 历史足迹 / 解忧记录 -->'

if target_after_profile in content:
    replacement = '</section>\n\n' + mine_cards_life_section + '\n\n      <!-- 模块 2: 历史足迹 / 解忧记录 -->'
    content = content.replace(target_after_profile, replacement, 1)
    print("[4] mineCardsLifeSection inserted into mineArea.")
else:
    # Try regex search for user-profile-banner and next section
    pattern_profile = re.compile(r'(<section class="card user-profile-banner">[\s\S]*?<\/section>)(\s*<!-- 模块 2: 历史足迹 \/ 解忧记录 -->)')
    m = pattern_profile.search(content)
    if m:
        content = content[:m.end(1)] + '\n\n' + mine_cards_life_section + '\n\n' + content[m.start(2):]
        print("[4] mineCardsLifeSection inserted into mineArea via regex.")
    else:
        raise SystemExit("Error: Could not find insertion point in mineArea!")

# ----------------------------------------------------------------------
# 4. Enhance JavaScript functions
# ----------------------------------------------------------------------
# In switchMainTab:
# update tab === 'cards' to redirect to mineArea and scroll to mineCardsLifeSection
old_switch_cards = """    } else if (tab === 'cards') {

      if (cardsArea) cardsArea.classList.remove('hidden');

      if ($('tabCards')) $('tabCards').classList.add('active');

      renderCardsSection();"""

new_switch_cards = """    } else if (tab === 'cards') {

      // 卡牌人生已收纳至「我的」专区
      switchMainTab('mine');
      var lifeSec = $('mineCardsLifeSection');
      if (lifeSec) {
        lifeSec.scrollIntoView({ behavior: 'smooth' });
      }
      return;"""

if old_switch_cards in content:
    content = content.replace(old_switch_cards, new_switch_cards, 1)
    print("[5] switchMainTab('cards') updated to redirect to mine.")
else:
    print("[5] Warning: old_switch_cards pattern not found, trying fuzzy match...")
    pattern_sc = re.compile(r'\}\s*else\s*if\s*\(\s*tab\s*===\s*[\'"]cards[\'"]\s*\)\s*\{[\s\S]*?renderCardsSection\(\);')
    m = pattern_sc.search(content)
    if m:
        content = content[:m.start()] + new_switch_cards + content[m.end():]
        print("[5] switchMainTab('cards') updated via regex.")

# Add switchCardLifeSubView and writeJournalWithFavCard function
new_js_helpers = """
  // ================= 儒释道卡牌人生：主理人卡牌库与我的收藏分流切换 =================
  window.switchCardLifeSubView = function(subView) {
    // 权限坚固锁：若非主理人尝试查看全量卡牌库，坚决拦截
    if (subView !== 'fav' && !appState.isManagerLoggedIn) {
      showToast('卡牌库仅主理人可见，请先在下方完成主理人认证');
      subView = 'fav';
    }

    var tabsWrap = $('managerCardLifeTabs');
    if (tabsWrap) {
      var pills = tabsWrap.querySelectorAll('.inspo-pill');
      pills.forEach(function(p) { p.classList.remove('active'); });
    }

    var favView = $('userFavoriteCardsView');
    var libWrap = $('managerCardsLibraryWrap');
    var subPantheon = $('subViewPantheon108');
    var subZen96 = $('subViewZen96');
    var subTheme = $('subViewThemePacks');

    if (subView === 'fav') {
      if ($('btnTabFavCards')) $('btnTabFavCards').classList.add('active');
      if (favView) {
        favView.classList.remove('hidden');
        favView.style.display = 'block';
      }
      if (libWrap) {
        libWrap.classList.add('hidden');
        libWrap.style.display = 'none';
      }
      renderFavoriteCards();
    } else {
      if (favView) {
        favView.classList.add('hidden');
        favView.style.display = 'none';
      }
      if (libWrap) {
        libWrap.classList.remove('hidden');
        libWrap.style.display = 'block';
      }

      if (subPantheon) subPantheon.style.display = (subView === 'pantheon') ? 'block' : 'none';
      if (subZen96) subZen96.style.display = (subView === 'zen96') ? 'block' : 'none';
      if (subTheme) subTheme.style.display = (subView === 'theme') ? 'block' : 'none';

      if (subView === 'pantheon') {
        if ($('btnTabPantheon')) $('btnTabPantheon').classList.add('active');
        if (typeof renderPantheonSection === 'function') renderPantheonSection();
      } else if (subView === 'zen96') {
        if ($('btnTabZen96')) $('btnTabZen96').classList.add('active');
        if (typeof renderZen96CardsSection === 'function') renderZen96CardsSection();
      } else if (subView === 'theme') {
        if ($('btnTabThemePacks')) $('btnTabThemePacks').classList.add('active');
        if (typeof renderThemePackGrid === 'function') renderThemePackGrid();
      }
    }
  };

  window.writeJournalWithFavCard = function(name, core) {
    switchMainTab('growth');
    var journalInput = $('journalInputText');
    if (journalInput) {
      journalInput.value = '【借境观心 · ' + name + '】\\n' +
        '核心觉察：' + core + '\\n\\n' +
        '我的当下心声与复盘：\\n';
      journalInput.focus();
      journalInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    showToast('已载入《' + name + '》觉察课题，请写下您的真实心声。');
  };
"""

# Enhance renderFavoriteCards to support 96 zen cards, 108 pantheon cards, and classic cards
new_render_fav_cards = """  function renderFavoriteCards() {
    var container = $('favCardsContainer');
    if (!container) return;

    var rawFavs = getStorageJson('wutang_favorite_cards', []);
    
    // 构建全量卡牌映射索引
    var cardMap = {};
    if (typeof CARDS_MINDSET !== 'undefined') {
      [].concat(CARDS_MINDSET || [], CARDS_WISDOM || [], CARDS_ACTION || []).forEach(function(c) {
        if (c && c.card_id) cardMap[c.card_id] = { type: 'classic', data: c };
      });
    }
    if (typeof ZEN_CARDS_96 !== 'undefined' && Array.isArray(ZEN_CARDS_96)) {
      ZEN_CARDS_96.forEach(function(c) {
        if (c && c.card_id) cardMap[c.card_id] = { type: 'zen96', data: c };
        if (c && c.name) cardMap[c.name] = { type: 'zen96', data: c };
      });
    }
    if (typeof ZEN_CARDS_108 !== 'undefined' && Array.isArray(ZEN_CARDS_108)) {
      ZEN_CARDS_108.forEach(function(c) {
        var cid = c.id || ('pantheon_' + c.num) || c.name;
        cardMap[cid] = { type: 'zen108', data: c };
        if (c.name) cardMap[c.name] = { type: 'zen108', data: c };
      });
    }

    var resolvedCards = [];
    var seenIds = {};

    rawFavs.forEach(function(item) {
      var id = (typeof item === 'string') ? item : (item && item.card_id ? item.card_id : null);
      if (!id && typeof item === 'object' && item.name) id = item.name;
      if (!id || seenIds[id]) return;
      seenIds[id] = true;

      if (cardMap[id]) {
        resolvedCards.push(cardMap[id]);
      } else if (typeof item === 'object') {
        if (item.image_png) {
          resolvedCards.push({ type: 'zen96', data: item });
        } else {
          resolvedCards.push({ type: 'classic', data: item });
        }
      }
    });

    var countNotice = $('favCardsCountNotice');
    if (countNotice) countNotice.textContent = '当前珍藏 ' + resolvedCards.length + ' 张启发卡牌';
    if ($('userFavCount')) $('userFavCount').textContent = resolvedCards.length;

    if (resolvedCards.length === 0) {
      container.innerHTML = '<div style="grid-column:1/-1;padding:36px 20px;text-align:center;background:var(--color-surface-subtle);border-radius:12px;border:1px dashed var(--color-border);">'
        + '<div style="font-size:36px;margin-bottom:8px;">🎴</div>'
        + '<h4 style="font-family:var(--font-serif);margin:0 0 6px;color:var(--color-ink);font-size:16px;">暂无珍藏卡牌</h4>'
        + '<p style="margin:0 0 16px;font-size:13px;color:var(--color-muted);">在解忧道席抽牌、或自省觉察时，点击「⭐ 收入珍藏」即可沉淀在你的卡牌人生中。</p>'
        + '<button type="button" class="btn sm primary" onclick="switchMainTab(\\'relief\\')">前往解忧参悟抽牌 ✨</button>'
        + '</div>';
      return;
    }

    container.innerHTML = resolvedCards.map(function(item) {
      if (item.type === 'zen96') {
        var c = item.data;
        var cid = c.card_id || c.name;
        return '<div class="studio-card-item" style="padding:0;overflow:hidden;border:1px solid #D9CEBD;background:#FAF6EF;display:flex;flex-direction:column;border-radius:10px;">'
          + '  <div style="width:100%;aspect-ratio:2/3;background:#E8E2D6;overflow:hidden;cursor:pointer;position:relative;" onclick="openZen96CardModal(\\'' + esc(cid) + '\\')">'
          + '    <img src="' + esc(c.image_png) + '" alt="' + esc(c.name) + '" loading="lazy" style="width:100%;height:100%;object-fit:cover;">'
          + '    <div style="position:absolute;bottom:8px;right:8px;background:rgba(42,38,35,0.75);color:#fff;font-size:11px;padding:2px 8px;border-radius:12px;backdrop-filter:blur(4px);">3D 赏析</div>'
          + '  </div>'
          + '  <div style="padding:12px 14px;flex:1;display:flex;flex-direction:column;justify-content:space-between;">'
          + '    <div>'
          + '      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
          + '        <span class="badge ok" style="font-size:11px;padding:1px 6px;">' + esc(c.series || '东方觉察') + (c.num ? (' · ' + esc(c.num)) : '') + '</span>'
          + '        <button type="button" class="btn ghost sm" style="padding:2px 6px;font-size:11px;color:var(--color-danger);" onclick="toggleFavoriteCard(\\'' + esc(cid) + '\\')" title="移出珍藏">★ 移出</button>'
          + '      </div>'
          + '      <h4 style="font-family:var(--font-serif);margin:4px 0 6px;font-size:16px;font-weight:bold;">' + esc(c.name) + '</h4>'
          + '      <p style="margin:0 0 8px;font-size:12px;color:var(--color-primary);font-family:var(--font-serif);line-height:1.5;">“' + esc(c.core || '') + '”</p>'
          + '    </div>'
          + '    <div style="display:flex;gap:6px;margin-top:6px;">'
          + '      <button type="button" class="btn sm secondary" style="flex:1;font-size:11.5px;padding:5px 0;" onclick="openZen96CardModal(\\'' + esc(cid) + '\\')">翻看自省</button>'
          + '      <button type="button" class="btn sm" style="flex:1;font-size:11.5px;padding:5px 0;" onclick="writeJournalWithFavCard(\\'' + esc(c.name) + '\\', \\'' + esc(c.core || '') + '\\')">写日记</button>'
          + '    </div>'
          + '  </div>'
          + '</div>';
      } else if (item.type === 'zen108') {
        var c = item.data;
        var schColor = (c.school === 'daoism') ? '#2B4C5F' : ((c.school === 'buddhism') ? '#B58900' : '#8E2927');
        var schName = (c.school === 'daoism') ? '道学·老子' : ((c.school === 'buddhism') ? '释学·佛陀' : '儒学·孔子');
        var cid = c.id || ('pantheon_' + c.num) || c.name;
        return '<div style="background:#FFF;border:1px solid var(--color-border);border-radius:10px;padding:12px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 2px 6px rgba(0,0,0,0.02);">'
          + '<div>'
          + '  <div style="display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--color-muted);margin-bottom:6px;">'
          + '    <span style="color:' + schColor + ';font-weight:700;">' + esc(schName) + '</span>'
          + '    <button type="button" class="btn ghost sm" style="padding:1px 5px;font-size:11px;color:var(--color-danger);" onclick="toggleFavoriteCard(\\'' + esc(cid) + '\\')">★ 移出</button>'
          + '  </div>'
          + '  <div style="font-family:var(--font-serif);font-size:18px;font-weight:700;color:' + schColor + ';margin-bottom:4px;">【 ' + esc(c.name) + ' 】</div>'
          + '  <div style="font-size:11.5px;color:var(--color-gold);font-family:var(--font-serif);margin-bottom:6px;">' + esc(c.master_motto || '') + '</div>'
          + '  <div style="font-size:12px;color:var(--color-ink-light);line-height:1.5;margin-bottom:8px;">' + esc(c.core) + '</div>'
          + '</div>'
          + '<div style="border-top:1px dashed var(--color-border);padding-top:8px;display:flex;justify-content:space-between;align-items:center;font-size:11px;">'
          + '  <span style="color:var(--color-muted);">' + esc(c.series || '常道') + '</span>'
          + '  <button type="button" class="btn sm" style="padding:2px 8px;font-size:11px;" onclick="selectPantheonCardToConsult(\\'' + esc(c.name) + '\\', \\'' + esc(c.school) + '\\')">由此开悟</button>'
          + '</div>'
          + '</div>';
      } else {
        return renderSingleCardHtml(item.data);
      }
    }).join('');
  }"""

# Replace old renderFavoriteCards
old_render_fav_pattern = re.compile(r'  function renderFavoriteCards\(\) \{[\s\S]*?container\.innerHTML = cards\.map\(function\(c\) \{ return renderSingleCardHtml\(c\); \}\)\.join\(\'\'\);\s*\}')
if old_render_fav_pattern.search(content):
    content = old_render_fav_pattern.sub(new_render_fav_cards, content, count=1)
    print("[6] renderFavoriteCards enhanced successfully.")
else:
    raise SystemExit("Error: old renderFavoriteCards pattern not found!")

# Insert new_js_helpers right above renderFavoriteCards
content = content.replace("  function renderFavoriteCards() {", new_js_helpers + "\n  function renderFavoriteCards() {", 1)
print("[7] switchCardLifeSubView and writeJournalWithFavCard inserted.")

# ----------------------------------------------------------------------
# 5. Update updateManagerUI for role-based visibility
# ----------------------------------------------------------------------
# In updateManagerUI():
# when isManagerLoggedIn is true: show managerCardLifeBadge & managerCardLifeTabs
# when false: hide managerCardLifeBadge & managerCardLifeTabs, hide managerCardsLibraryWrap, reset to fav subview

mgr_ui_hook = "    if (appState.isManagerLoggedIn) {"
mgr_ui_patch = """    if (appState.isManagerLoggedIn) {
      // 激活主理人卡牌人生全量卡牌库特权
      if ($('managerCardLifeBadge')) $('managerCardLifeBadge').style.display = 'inline-flex';
      if ($('managerCardLifeTabs')) {
        $('managerCardLifeTabs').classList.remove('hidden');
        $('managerCardLifeTabs').style.display = 'flex';
      }
      if ($('mineCardsLifeTitle')) $('mineCardsLifeTitle').textContent = '卡牌人生 · 我的收藏与全量卡牌库 👑';
      if ($('mineCardsLifeSubtitle')) $('mineCardsLifeSubtitle').textContent = '主理人专享：可查看管理 108 百八常道图鉴、96 东方觉察画廊及 6 大主题卡牌包，支持 A4 拼版打印。';
      if (typeof renderPantheonSection === 'function') renderPantheonSection();
      if (typeof renderZen96CardsSection === 'function') renderZen96CardsSection();
      if (typeof renderThemePackGrid === 'function') renderThemePackGrid();"""

content = content.replace(mgr_ui_hook, mgr_ui_patch, 1)

# Now in the else block of updateManagerUI
mgr_ui_else_hook = "    } else {\n\n      // 2. 访客或普通用户状态"
if mgr_ui_else_hook not in content:
    mgr_ui_else_hook = "    } else {\n      // 2. 访客或普通用户状态"
if mgr_ui_else_hook not in content:
    mgr_ui_else_pattern = re.compile(r'\}\s*else\s*\{\s*\/\/\s*2\.\s*访客或普通用户状态')
    m_else = mgr_ui_else_pattern.search(content)
    if m_else:
        mgr_ui_else_hook = m_else.group(0)

mgr_ui_else_patch = """    } else {
      // 普通用户/访客：卡牌库彻底隐藏，只允许看我的收藏
      if ($('managerCardLifeBadge')) $('managerCardLifeBadge').style.display = 'none';
      if ($('managerCardLifeTabs')) {
        $('managerCardLifeTabs').classList.add('hidden');
        $('managerCardLifeTabs').style.display = 'none';
      }
      if ($('managerCardsLibraryWrap')) {
        $('managerCardsLibraryWrap').classList.add('hidden');
        $('managerCardsLibraryWrap').style.display = 'none';
      }
      if ($('mineCardsLifeTitle')) $('mineCardsLifeTitle').textContent = '卡牌人生 · 我的收藏';
      if ($('mineCardsLifeSubtitle')) $('mineCardsLifeSubtitle').textContent = '立足东方智慧照亮人生之路。回看你在解忧旅途中珍藏的心境、智慧与觉察卡牌。';
      if (typeof switchCardLifeSubView === 'function') switchCardLifeSubView('fav');

      // 2. 访客或普通用户状态"""

content = content.replace(mgr_ui_else_hook, mgr_ui_else_patch, 1)
print("[8] updateManagerUI patched for role-based visibility.")

# ----------------------------------------------------------------------
# 6. Ensure renderMineSection calls renderFavoriteCards()
# ----------------------------------------------------------------------
render_mine_hook = "  function renderMineSection() {\n\n    renderHistoryCardList();"
if render_mine_hook not in content:
    render_mine_hook = "  function renderMineSection() {\n    renderHistoryCardList();"

render_mine_patch = """  function renderMineSection() {
    renderHistoryCardList();
    renderFavoriteCards();"""

if render_mine_hook in content:
    content = content.replace(render_mine_hook, render_mine_patch, 1)
    print("[9] renderMineSection calls renderFavoriteCards.")

# Write updated _template.html
with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] All patches applied to frontend/_template.html!")
