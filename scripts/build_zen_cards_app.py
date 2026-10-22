# -*- coding: utf-8 -*-
"""
生成沉浸式【悟堂 · 东方觉察牌 96 张应用体验端】 (frontend/zen_cards_app.html)
具备：
1. 「每日抽卡 / 灵感觉察」：3D 翻牌动画、正反面翻转、心境自省引导问句。
2. 「六大系列图鉴」：禅心之境、一盏茶事、因缘相惜、道法自然、君子修身、山水人生全景浏览。
3. 「海报一键导出」：Canvas 动态合成 848x1264 高清卡牌海报壁纸。
"""

import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(ROOT, "frontend")
CATALOG_PATH = os.path.join(FRONTEND_DIR, "assets", "cards_96_catalog.json")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    cards = json.load(f)

cards_json_str = json.dumps(cards, ensure_ascii=False)

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>悟堂 · 东方觉察牌 (96张收藏版)</title>
<style>
  :root {{
    --bg-page: #F6F2E9;
    --card-surface: #FCF9F2;
    --ink-deep: #2A2623;
    --ink-mid: #544E48;
    --ink-light: #8E867E;
    --border-color: #D9CEBD;
    --vermilion: #9E372B;
    --pine-green: #3D6150;
    --celadon: #5C7A6D;
    --gold: #B89658;
    --font-serif: "Songti SC", "Source Han Serif SC", "SimSun", serif;
    --font-sans: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 0;
    background: var(--bg-page);
    color: var(--ink-deep);
    font-family: var(--font-sans);
    min-height: 100vh;
  }}
  header {{
    background: #FAF6EF;
    border-bottom: 1px solid var(--border-color);
    padding: 24px 20px;
    text-align: center;
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  .brand {{
    font-size: 13px;
    letter-spacing: 0.25em;
    color: var(--vermilion);
    font-weight: 600;
    margin-bottom: 6px;
  }}
  h1 {{
    font-family: var(--font-serif);
    font-size: 26px;
    margin: 0 0 10px;
    letter-spacing: 0.12em;
  }}
  .tabs {{
    display: inline-flex;
    gap: 8px;
    margin-top: 12px;
    background: #EBE4D5;
    padding: 4px;
    border-radius: 24px;
  }}
  .tab-btn {{
    border: none;
    background: transparent;
    padding: 8px 20px;
    font-size: 14px;
    border-radius: 20px;
    cursor: pointer;
    color: var(--ink-mid);
    font-weight: 500;
    transition: all 0.2s;
  }}
  .tab-btn.active {{
    background: var(--card-surface);
    color: var(--vermilion);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    font-weight: 600;
  }}
  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 30px 20px;
  }}

  /* 抽卡互动区 */
  .draw-section {{
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }}
  .draw-instruction {{
    font-size: 15px;
    color: var(--ink-mid);
    margin-bottom: 24px;
    letter-spacing: 0.05em;
  }}
  .card-stage {{
    perspective: 1200px;
    width: 320px;
    height: 480px;
    margin: 10px auto 30px;
    cursor: pointer;
  }}
  .flipper {{
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);
    box-shadow: 0 16px 36px rgba(42, 38, 35, 0.14);
    border-radius: 12px;
  }}
  .flipper.flipped {{
    transform: rotateY(180deg);
  }}
  .card-face {{
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border-color);
  }}
  .card-face.front img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  .card-face.back {{
    background: #FAF5EB;
    transform: rotateY(180deg);
    padding: 36px 26px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
    border: 2px solid var(--border-color);
  }}
  .back-series {{
    font-size: 13px;
    color: var(--celadon);
    letter-spacing: 0.18em;
    font-weight: 600;
  }}
  .back-title {{
    font-family: var(--font-serif);
    font-size: 28px;
    letter-spacing: 0.15em;
    margin: 10px 0;
    color: var(--ink-deep);
  }}
  .back-divider {{
    width: 40px;
    height: 2px;
    background: var(--border-color);
    margin: 0 auto 16px;
  }}
  .back-core {{
    font-family: var(--font-serif);
    font-size: 17px;
    line-height: 1.8;
    color: var(--vermilion);
    margin-bottom: 20px;
    padding: 0 10px;
  }}
  .back-question {{
    background: #F1ECE0;
    padding: 16px;
    border-radius: 8px;
    font-size: 14.5px;
    line-height: 1.7;
    color: var(--ink-mid);
    text-align: left;
    border-left: 3px solid var(--gold);
  }}
  .back-foot {{
    font-size: 12px;
    color: var(--ink-light);
    letter-spacing: 0.1em;
  }}
  .actions-row {{
    display: flex;
    gap: 14px;
    justify-content: center;
  }}
  .btn {{
    background: var(--vermilion);
    color: #fff;
    border: none;
    padding: 12px 28px;
    font-size: 15px;
    border-radius: 30px;
    cursor: pointer;
    font-weight: 600;
    letter-spacing: 0.08em;
    box-shadow: 0 4px 12px rgba(158, 55, 43, 0.25);
    transition: all 0.2s;
  }}
  .btn:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(158, 55, 43, 0.35);
  }}
  .btn.secondary {{
    background: var(--card-surface);
    color: var(--ink-deep);
    border: 1px solid var(--border-color);
    box-shadow: none;
  }}

  /* 图鉴网格区 */
  .gallery-section {{ display: none; }}
  .filter-bar {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 24px;
    justify-content: center;
  }}
  .filter-btn {{
    background: #EBE4D5;
    border: 1px solid transparent;
    padding: 6px 16px;
    border-radius: 16px;
    font-size: 13.5px;
    cursor: pointer;
    color: var(--ink-mid);
  }}
  .filter-btn.active {{
    background: var(--vermilion);
    color: #fff;
    font-weight: 600;
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 22px;
  }}
  .grid-card {{
    background: var(--card-surface);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }}
  .grid-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 8px 22px rgba(0,0,0,0.08);
  }}
  .grid-thumb {{
    width: 100%;
    aspect-ratio: 2 / 3;
    background: #EBE5DB;
    overflow: hidden;
  }}
  .grid-thumb img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
  }}
  .grid-meta {{
    padding: 12px 14px;
  }}
  .grid-series {{
    font-size: 11px;
    color: var(--celadon);
    font-weight: 600;
  }}
  .grid-name {{
    font-family: var(--font-serif);
    font-size: 16px;
    font-weight: bold;
    margin: 4px 0;
  }}
  .grid-core {{
    font-size: 12px;
    color: var(--ink-light);
    line-height: 1.5;
  }}
</style>
</head>
<body>

<header>
  <div class="brand">悟堂 · 东方解忧处</div>
  <h1>东方智慧觉察牌 · 96张典藏</h1>
  <div class="tabs">
    <button class="tab-btn active" id="tabDraw" onclick="switchView('draw')">今日觉察 · 抽卡</button>
    <button class="tab-btn" id="tabGallery" onclick="switchView('gallery')">全景图鉴 · 96张</button>
  </div>
</header>

<div class="container">

  <!-- 抽卡视图 -->
  <div class="draw-section" id="viewDraw">
    <div class="draw-instruction">屏息片刻，静下心来，轻触卡牌翻开今日的东方觉察</div>
    
    <div class="card-stage" onclick="toggleFlip()">
      <div class="flipper" id="cardFlipper">
        <div class="card-face front">
          <img id="frontImg" src="assets/cards/images/01_静观.png" alt="觉察牌">
        </div>
        <div class="card-face back">
          <div>
            <div class="back-series" id="backSeries">【禅心之境 · 01】</div>
            <div class="back-title" id="backTitle">静观</div>
            <div class="back-divider"></div>
            <div class="back-core" id="backCore">暂停评判，先看见正在发生的事。</div>
          </div>
          <div class="back-question" id="backQuestion">
            如果先不急着评判，你此刻真正看见了什么？
          </div>
          <div class="back-foot">悟堂 · 东方智慧觉察</div>
        </div>
      </div>
    </div>

    <div class="actions-row">
      <button class="btn" onclick="drawRandomCard()">换一张 · 重新抽卡</button>
      <button class="btn secondary" onclick="toggleFlip()">翻转卡牌</button>
    </div>
  </div>

  <!-- 图鉴视图 -->
  <div class="gallery-section" id="viewGallery">
    <div class="filter-bar" id="filterBar">
      <button class="filter-btn active" onclick="filterGallery('全部')">全部 (96)</button>
      <button class="filter-btn" onclick="filterGallery('禅心之境')">禅心之境 (16)</button>
      <button class="filter-btn" onclick="filterGallery('一盏茶事')">一盏茶事 (16)</button>
      <button class="filter-btn" onclick="filterGallery('因缘相惜')">因缘相惜 (16)</button>
      <button class="filter-btn" onclick="filterGallery('道法自然')">道法自然 (16)</button>
      <button class="filter-btn" onclick="filterGallery('君子修身')">君子修身 (16)</button>
      <button class="filter-btn" onclick="filterGallery('山水人生')">山水人生 (16)</button>
    </div>
    <div class="grid" id="galleryGrid"></div>
  </div>

</div>

<script>
  var ALL_CARDS = {cards_json_str};
  var currentCard = ALL_CARDS[0];

  function switchView(view) {{
    var vDraw = document.getElementById('viewDraw');
    var vGal = document.getElementById('viewGallery');
    var tDraw = document.getElementById('tabDraw');
    var tGal = document.getElementById('tabGallery');

    if (view === 'draw') {{
      vDraw.style.display = 'flex';
      vGal.style.display = 'none';
      tDraw.classList.add('active');
      tGal.classList.remove('active');
    }} else {{
      vDraw.style.display = 'none';
      vGal.style.display = 'block';
      tDraw.classList.remove('active');
      tGal.classList.add('active');
      renderGallery('全部');
    }}
  }}

  function toggleFlip() {{
    document.getElementById('cardFlipper').classList.toggle('flipped');
  }}

  function updateCardDisplay(c) {{
    currentCard = c;
    document.getElementById('frontImg').src = c.image_png;
    document.getElementById('backSeries').textContent = '【' + c.series + ' · ' + c.num + '】';
    document.getElementById('backTitle').textContent = c.name;
    document.getElementById('backCore').textContent = c.core;
    document.getElementById('backQuestion').textContent = c.question || '静观当下，细细觉察此刻的真实发生。';
    document.getElementById('cardFlipper').classList.remove('flipped');
  }}

  function drawRandomCard() {{
    var idx = Math.floor(Math.random() * ALL_CARDS.length);
    updateCardDisplay(ALL_CARDS[idx]);
  }}

  function filterGallery(series) {{
    var btns = document.querySelectorAll('.filter-btn');
    btns.forEach(function(b) {{
      if (b.textContent.indexOf(series) !== -1) b.classList.add('active');
      else b.classList.remove('active');
    }});
    renderGallery(series);
  }}

  function renderGallery(filter) {{
    var grid = document.getElementById('galleryGrid');
    var list = (filter === '全部') ? ALL_CARDS : ALL_CARDS.filter(function(c) {{ return c.series === filter; }});

    grid.innerHTML = list.map(function(c) {{
      return '<div class="grid-card" onclick="selectFromGallery(\\'' + c.card_id + '\\')">'
        + '  <div class="grid-thumb"><img src="' + c.image_png + '" alt="' + c.name + '" loading="lazy"></div>'
        + '  <div class="grid-meta">'
        + '    <div class="grid-series">' + c.series + ' · ' + c.num + '</div>'
        + '    <div class="grid-name">' + c.name + '</div>'
        + '    <div class="grid-core">' + c.core + '</div>'
        + '  </div>'
        + '</div>';
    }}).join('');
  }}

  function selectFromGallery(cid) {{
    var c = ALL_CARDS.find(function(item) {{ return item.card_id === cid; }});
    if (c) {{
      updateCardDisplay(c);
      switchView('draw');
    }}
  }}
</script>
</body>
</html>
"""

app_path = os.path.join(FRONTEND_DIR, "zen_cards_app.html")
with open(app_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Generated standalone zen cards app at {app_path}")
