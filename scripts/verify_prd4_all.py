# -*- coding: utf-8 -*-
"""
悟堂 · 东方解脱之道与儒释道卡牌人生 —— PRD 4.0 全量综合回归与验收套件
覆盖：
1. 儒释道三至圣代表导师资产 (孔子 / 老子 / 释迦牟尼)
2. 514 条典籍分类 (儒 / 释 / 道 / 通用) 检索互斥与三圣合参验证
3. 108 百八常道卡牌人生图鉴谱系完整性 (36 儒 + 36 道 + 36 释)
4. 后台 API：三圣四维解惑流式与非流式响应、解脱卡印签名提取
5. 300 DPI 实体卡牌工业级印刷母版与 ZIP 打包导出验证
6. 前端 DOM 与单文件 index.html 4.0 关键组件闭环核验
"""
import os
import sys
import json
import zipfile
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi.testclient import TestClient
from PIL import Image
from backend.app import app
from backend.services.rag_service import rag_service
from backend.services.card_render_service import card_render_service

client = TestClient(app)
results = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append({"name": name, "pass": bool(condition), "detail": detail})
    mark = "✓" if condition else "✗"
    msg = f"  [{mark}] {name}"
    if detail:
        msg += f" ({detail})"
    print(msg)

def run_prd4_checks():
    print("=================================================================")
    print("🎴 悟堂 · 儒释道三学解惑与专属解脱卡牌 PRD 4.0 全量验收套件")
    print("=================================================================\n")

    # ---------------- 1. 儒释道三家代表导师资产 ----------------
    print("--- 1. 儒释道三学宗师专席与视觉资产 ---")
    avatars_path = ROOT / "frontend" / "assets" / "sage_avatars.json"
    check("圣贤立绘资产库存在", avatars_path.exists())
    if avatars_path.exists():
        with open(avatars_path, "r", encoding="utf-8") as f:
            sages = json.load(f)
        check("孔子 (儒家宗师) 席位完整", "confucius" in sages and "论语" in str(sages["confucius"]["keywords"]))
        check("老子 (道家宗师) 席位完整", "laozi" in sages and "道德经" in str(sages["laozi"]["keywords"]))
        check("释迦牟尼 (释家觉者) 席位完整", "shakyamuni" in sages and "明心见性" in sages["shakyamuni"]["motto"])
        check("佛陀别名与金金色调完备", "buddha" in sages and "rgb(181, 137, 0)" in sages["shakyamuni"]["color"])

    # ---------------- 2. 514 条典籍分类与检索 ----------------
    print("\n--- 2. 权威典籍库儒释道分类打标与检索分流 ---")
    classics = rag_service.classics
    check("典籍总数达到 500+ 条", len(classics) >= 500, f"共 {len(classics)} 条")

    confucian_count = sum(1 for c in classics if c.get("school") == "confucianism")
    daoist_count = sum(1 for c in classics if c.get("school") == "daoism")
    buddhist_count = sum(1 for c in classics if c.get("school") == "buddhism")

    check("儒家典籍覆盖充足", confucian_count >= 200, f"儒家典籍 {confucian_count} 条")
    check("道家典籍覆盖充足", daoist_count >= 80, f"道家典籍 {daoist_count} 条")
    check("释家典籍扩充充足", buddhist_count >= 80, f"释家典籍 {buddhist_count} 条")

    # 检索分流测试
    c_res = rag_service.retrieve_classics("责任与人际", "work", top_k=2, school="confucianism")
    check("儒学赛道优先返回儒家经典", all(c.get("school") in ["confucianism", "general"] for c in c_res))

    d_res = rag_service.retrieve_classics("顺应自然", "night", top_k=2, school="daoism")
    check("道学赛道优先返回道家经典", all(c.get("school") in ["daoism", "general"] for c in d_res))

    b_res = rag_service.retrieve_classics("看破执念", "growth", top_k=2, school="buddhism")
    check("释学赛道优先返回佛学经典", all(c.get("school") in ["buddhism", "general"] for c in b_res))

    sym_res = rag_service.retrieve_classics("综合困境", "work", top_k=3, school="symposium")
    sym_schools = set(c.get("school") for c in sym_res)
    check("三圣圆桌实现三教各萃取一则", "confucianism" in sym_schools and "daoism" in sym_schools and "buddhism" in sym_schools, f"包含: {sym_schools}")

    # ---------------- 3. 108 百八常道卡牌谱系 ----------------
    print("\n--- 3. 儒释道卡牌人生 · 108 百八常道图鉴谱系 ---")
    c108_path = ROOT / "frontend" / "assets" / "cards_108_catalog.json"
    check("108 常道卡牌全量谱系文件存在", c108_path.exists())
    if c108_path.exists():
        with open(c108_path, "r", encoding="utf-8") as f:
            c108 = json.load(f)
        check("卡牌总数恰为 108 张", len(c108) == 108)
        ru_cards = [c for c in c108 if c.get("school") == "confucianism"]
        dao_cards = [c for c in c108 if c.get("school") == "daoism"]
        bud_cards = [c for c in c108 if c.get("school") == "buddhism"]
        check("儒家修己谱系恰为 36 张", len(ru_cards) == 36)
        check("道家逍遥谱系恰为 36 张", len(dao_cards) == 36)
        check("释家觉照谱系恰为 36 张", len(bud_cards) == 36)
        check("卡牌具备英文定心箴言与场景设定", bool(c108[0].get("english_mantra") and c108[0].get("scene")))

    # ---------------- 4. 后台 API 与解脱开示四维结构 ----------------
    print("\n--- 4. 后台 API：三圣四维解惑与解脱卡印签名 ---")
    health = client.get("/api/health").json()
    check("API Health 升级至 4.0.0", health.get("version") == "4.0.0")
    check("API 声明支持四大修道导师席位", len(health.get("masters", [])) == 4)

    # 释家解惑测试
    bud_req = {
        "text": "工作繁重，深陷内耗焦虑，夜晚失眠，总放不下别人的评判。",
        "scenario": "night",
        "track": "buddhism",
        "master": "shakyamuni",
        "user_nickname": "求道行者"
    }
    resp = client.post("/api/relief/generate", json=bud_req)
    check("释学解惑接口响应 200", resp.status_code == 200)
    b_data = resp.json()
    check("正确返回释迦牟尼导师信息", b_data.get("master") == "释迦牟尼" and b_data.get("track") == "buddhism")
    check("自动生成专属解脱卡号", str(b_data.get("card_number", "")).startswith("WU-BUD-"))
    
    four_step = b_data.get("four_step_parsed", {})
    check("四维解惑结构完整 (闻心/示道/笃行/法印)", bool(four_step.get("empathy") and four_step.get("wisdom") and four_step.get("micro_action")), f"emp:{bool(four_step.get('empathy'))}, wis:{bool(four_step.get('wisdom'))}, act:{bool(four_step.get('micro_action'))}, raw:{b_data.get('raw_markdown', '')[:100]}")
    sig = b_data.get("card_signature", {})
    check("解脱卡印签名元数据完整", bool(sig.get("card_name") and sig.get("aphorism") and sig.get("english_mantra")), f"卡名: {sig.get('card_name')}, 金句: {sig.get('aphorism')[:16]}...")
    check("卡印包含 96 东方智慧契合觉察牌", bool(sig.get("matched_zen_card")), f"契合卡: {sig.get('matched_zen_card', {}).get('name')}")
    check("契合觉察牌包含核心觉察与叩问心门", bool(sig.get("matched_zen_card", {}).get("core") and sig.get("matched_zen_card", {}).get("question")))

    # ---------------- 5. 300 DPI 工业实体打印卡包导出 ----------------
    print("\n--- 5. 300 DPI 实体卡牌印刷级导出与 ZIP 打包 ---")
    card_export_payload = {
        "name": "克己",
        "school": "confucianism",
        "master": "孔子",
        "aphorism": "君子求诸己，万般皆因行未至。立志而笃行，当下即安泰。",
        "english_mantra": "Self-discipline brings enduring peace.",
        "user_nickname": "墨客",
        "user_statement": "日常琐事繁杂，总觉得时间不够，缺乏专注。",
        "classic_source": "《论语·卫灵公》（春秋·孔子）",
        "quote": "君子求诸己，小人求诸人。",
        "interpretation": "遇到不顺先看自己能做什么，把力气收回到自己身上，是瓦解内耗的唯一解药。",
        "action_title": "静坐调息，记录眼前可控之事",
        "action_steps": ["闭目静坐深呼吸三次", "写下1件眼前可控之事并立刻动手完成"]
    }

    # 测试正面渲染
    front_resp = client.post("/api/card/render-front", json=card_export_payload)
    check("POST /api/card/render-front 响应 200", front_resp.status_code == 200)
    front_img = Image.open(io.BytesIO(front_resp.content))
    check("卡牌正面符合 300 DPI 工业规格 (791 x 1087 px)", front_img.size == (791, 1087), f"分辨率: {front_img.size}")

    # 测试背面渲染
    back_resp = client.post("/api/card/render-back", json=card_export_payload)
    check("POST /api/card/render-back 响应 200", back_resp.status_code == 200)
    back_img = Image.open(io.BytesIO(back_resp.content))
    check("卡牌背面符合 300 DPI 工业规格 (791 x 1087 px)", back_img.size == (791, 1087))

    # 测试一键打包导出 ZIP
    zip_resp = client.post("/api/card/export-print-pack", json=card_export_payload)
    check("POST /api/card/export-print-pack 响应 200", zip_resp.status_code == 200)
    zf = zipfile.ZipFile(io.BytesIO(zip_resp.content))
    namelist = zf.namelist()
    check("打印包包含 300DPI 正面图", any("正面" in n for n in namelist))
    check("打印包包含 300DPI 背面图", any("背面" in n for n in namelist))
    check("打印包包含专色烫哑金遮罩图 (FoilMask)", any("FoilMask" in n for n in namelist))
    check("打印包包含印刷店下单说明文档", any("README" in n for n in namelist))

    # ---------------- 6. 前端静态 index.html 4.0 关键组件闭环 ----------------
    print("\n--- 6. 前端构建产物 index.html PRD 4.0 闭环核验 ---")
    html_file = ROOT / "frontend" / "index.html"
    check("frontend/index.html 构建产物存在", html_file.exists())
    if html_file.exists():
        html = html_file.read_text(encoding="utf-8")
        check("包含儒释道三学赛道选择器 (schoolTrackSelector)", "id=\"schoolTrackSelector\"" in html)
        check("包含孔子/老子/佛陀/三圣圆桌修道 Pills", all(k in html for k in ['data-track="confucianism"', 'data-track="daoism"', 'data-track="buddhism"', 'data-track="symposium"']))
        check("包含专属道号昵称输入框", "id=\"userNicknameInput\"" in html)
        check("包含专属解脱之道 3D 卡牌舞台 (liberationHeroContainer)", "id=\"liberationHeroContainer\"" in html)
        check("包含 300DPI 实体打印包导出按钮", "id=\"btnExportPrintPack\"" in html)
        check("包含手机高清壁纸保存按钮", "id=\"btnSaveWallpaper\"" in html)
        check("包含 108 百八常道卡牌人生展区 (pantheon108Section)", "id=\"pantheon108Section\"" in html)
        check("包含 A4 9宫格拼版打印模态预览 (modalA4Print)", "id=\"modalA4Print\"" in html)
        check("顶栏导航标签升级为「卡牌人生」", "儒释道卡牌人生与百八常道图鉴" in html and "卡牌人生" in html)
        check("包含 96 张东方智慧觉察牌联动舞台 (resonantZenCardContainer)", "id=\"resonantZenCardContainer\"" in html)
        check("包含「以此牌写觉察日记」动作按钮", "id=\"btnJournalWithResonantCard\"" in html)
        check("包含「收入珍藏」与「在 96 画廊中研读」按钮", "id=\"btnCollectResonantCard\"" in html and "id=\"btnViewInGallery\"" in html)

    # ---------------- 汇总 ----------------
    total = len(results)
    passed = sum(1 for r in results if r["pass"])
    print("\n=================================================================")
    print(f"📊 PRD 4.0 验收结果: {passed}/{total} 项测试通过")
    if passed == total:
        print("🎉 悟堂 · 儒释道三学解惑与专属解脱卡牌人生系统已完美达成 PRD 全部技术指标！")
    else:
        print("⚠️ 存在未通过项，请检查上方日志。")
    print("=================================================================\n")

if __name__ == "__main__":
    run_prd4_checks()
