# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 前端构建脚本
把 knowledge/classics.json + frontend/assets/wutang-data.json 内联进
frontend/_template.html，产出**单文件、可离线打开**的 frontend/index.html。

为什么内联：浏览器在 file:// 下会拦截 fetch() 读取本地 JSON（CORS），
内联可保证「双击打开就能跑」，对应验收点 A-08 / A-12（故障降级）。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    with open(os.path.join(ROOT, "frontend", "assets", "classics.json"), encoding="utf-8") as f:
        classics = json.load(f)
    with open(os.path.join(ROOT, "frontend", "assets", "wutang-data.json"), encoding="utf-8") as f:
        wd = json.load(f)

    cases = []
    cases_path = os.path.join(ROOT, "test_cases", "synthetic_normal_cases.csv")
    if os.path.exists(cases_path):
        import csv
        with open(cases_path, encoding="utf-8-sig") as f:
            cases = list(csv.DictReader(f))

    drafts = {}
    draft_dir = os.path.join(ROOT, "output", "article_drafts")
    if os.path.exists(draft_dir):
        for name in ["WUTANG-SYN-004", "WUTANG-SYN-007", "WUTANG-SYN-011"]:
            md_p = os.path.join(draft_dir, f"{name}.md")
            chk_p = os.path.join(draft_dir, f"{name}_checklist.md")
            if os.path.exists(md_p) and os.path.exists(chk_p):
                with open(md_p, encoding="utf-8") as f:
                    md_text = f.read()
                with open(chk_p, encoding="utf-8") as f:
                    chk_text = f.read()
                drafts[name] = {"content": md_text, "checklist": chk_text}

    sage_avatars = {}
    sage_path = os.path.join(ROOT, "frontend", "assets", "sage_avatars.json")
    if os.path.exists(sage_path):
        with open(sage_path, encoding="utf-8") as f:
            sage_avatars = json.load(f)

    payload = dict(
        classics=classics,
        scenarios=wd["scenarios"],
        microActions=wd["microActions"],
        brand=wd["brand"],
        riskHigh=wd["riskHigh"],
        riskReview=wd["riskReview"],
        riskPatterns=wd["riskPatterns"],
        syntheticCases=cases,
        articleDrafts=drafts,
        sageAvatars=sage_avatars,
    )
    # 内联时避免 </script> 破坏 HTML
    blob = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    with open(os.path.join(ROOT, "frontend", "_template.html"), encoding="utf-8") as f:
        html = f.read()

    if "__WUTANG_DATA__" not in html:
        raise SystemExit("[x] 模板缺少 __WUTANG_DATA__ 占位符")

    html = html.replace("__WUTANG_DATA__", blob)

    out = os.path.join(ROOT, "frontend", "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[ok] frontend/index.html  {len(html):,} 字符（数据已内联，可离线打开）")
    print(f"     语料 {len(classics)} 条 / 场景 {len(payload['scenarios'])} 个 / "
          f"高危词 {len(payload['riskHigh'])} / 复核词 {len(payload['riskReview'])}")


if __name__ == "__main__":
    main()
