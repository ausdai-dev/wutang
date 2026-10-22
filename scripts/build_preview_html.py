# -*- coding: utf-8 -*-
"""
生成东方智慧卡牌图鉴画廊 HTML
"""

import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "output")
CARDS_IMG_DIR = os.path.join(OUTPUT_DIR, "cards_images")
QUEUE_JSON = os.path.join(OUTPUT_DIR, "cards_queue.json")

with open(QUEUE_JSON, "r", encoding="utf-8") as f:
    queue = json.load(f)

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>悟堂 · 东方智慧卡牌 96 张生图看板 (848×1264)</title>
<style>
  :root {
    --bg: #F4EFE6;
    --card-bg: #FCF9F2;
    --ink: #2C2825;
    --muted: #7E7871;
    --border: #D8CEBE;
    --vermilion: #943A2F;
    --pine: #3B5B4C;
    --gold: #B5935B;
  }
  body {
    margin: 0;
    padding: 30px 20px;
    background: var(--bg);
    color: var(--ink);
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", serif;
  }
  header {
    text-align: center;
    max-width: 900px;
    margin: 0 auto 36px;
  }
  h1 {
    font-size: 28px;
    letter-spacing: 0.15em;
    margin-bottom: 8px;
    color: var(--ink);
  }
  .desc {
    font-size: 14px;
    color: var(--muted);
    letter-spacing: 0.08em;
  }
  .stats-bar {
    display: inline-flex;
    gap: 24px;
    margin-top: 18px;
    padding: 10px 28px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 30px;
    font-size: 14px;
  }
  .stats-item span {
    font-weight: bold;
    color: var(--vermilion);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 22px;
    max-width: 1400px;
    margin: 0 auto;
  }
  .card-item {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 14px rgba(44, 40, 37, 0.05);
    display: flex;
    flex-direction: column;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .card-item:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(44, 40, 37, 0.1);
  }
  .img-wrap {
    width: 100%;
    aspect-ratio: 2 / 3;
    background: #EBE5DB;
    overflow: hidden;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .placeholder {
    font-size: 13px;
    color: var(--muted);
    letter-spacing: 0.05em;
    padding: 20px;
    text-align: center;
  }
  .meta {
    padding: 14px 16px;
  }
  .badge {
    display: inline-block;
    font-size: 11px;
    padding: 2px 7px;
    border-radius: 4px;
    margin-bottom: 6px;
    background: #E8EFE9;
    color: var(--pine);
    font-weight: 500;
  }
  .title {
    font-size: 16px;
    font-weight: bold;
    margin: 0 0 4px;
  }
  .status {
    font-size: 12px;
    color: var(--muted);
  }
  .status.ok {
    color: var(--pine);
    font-weight: 600;
  }
</style>
</head>
<body>
<header>
  <h1>悟堂 · 东方智慧卡牌图鉴</h1>
  <div class="desc">96 张东方觉察牌 · 848×1264 纵向 2:3 超清原图 · 宋画水墨与工笔质感</div>
  <div class="stats-bar">
    <div class="stats-item">总计：96 张</div>
    <div class="stats-item">已完成：<span>""" + str(sum(1 for q in queue if q["status"] == "COMPLETED")) + """</span> 张</div>
    <div class="stats-item">待生成：<span>""" + str(sum(1 for q in queue if q["status"] == "PENDING")) + """</span> 张</div>
    <div class="stats-item">尺寸：<span>848 × 1264</span></div>
  </div>
</header>
<div class="grid">
"""

for q in queue:
    cid = q["id"]
    cname = q["name"]
    series = q["series"]
    status = q["status"]
    
    img_name = f"{cid}_{cname}.jpg"
    img_path = os.path.join(CARDS_IMG_DIR, img_name)
    
    if os.path.exists(img_path):
        rel_src = f"cards_images/{img_name}"
        img_tag = f'<img src="{rel_src}" alt="{cname}" loading="lazy">'
        status_tag = '<span class="status ok">✓ 848×1264 已就绪</span>'
    else:
        img_tag = f'<div class="placeholder">待生成<br>({series})</div>'
        status_tag = '<span class="status">队列中 · 待调度</span>'
        
    html += f"""
  <div class="card-item">
    <div class="img-wrap">{img_tag}</div>
    <div class="meta">
      <div class="badge">{series} · {cid}</div>
      <div class="title">{cname}</div>
      {status_tag}
    </div>
  </div>
"""

html += """
</div>
</body>
</html>
"""

html_path = os.path.join(OUTPUT_DIR, "cards_preview.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Generated preview html at {html_path}")
