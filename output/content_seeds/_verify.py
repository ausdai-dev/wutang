# -*- coding: utf-8 -*-
"""content_seeds 批次自检：引文逐字核对 + 状态 + 标识 + 行动牌存在性"""
import csv, json, re, os, sys

ROOT = r"C:\Users\ausda\.workbuddy\plugins\cache\my-experts\wutang-relief-team\1.0.0\skills\wutang-relief-engine"
SEEDS = r"D:\BaiduSyncdisk\02-DEV\悟堂\output\content_seeds"

with open(os.path.join(ROOT, "knowledge", "classics.csv"), encoding="utf-8-sig") as f:
    classics = {r["id"]: r for r in csv.DictReader(f)}
with open(os.path.join(ROOT, "knowledge", "cards_action.json"), encoding="utf-8") as f:
    actions = {c["card_id"] for c in json.load(f)}

files = sorted(x for x in os.listdir(SEEDS) if x.endswith(".md") and x != "manifest.md")
report = []
fail = 0

for fn in files:
    path = os.path.join(SEEDS, fn)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    issues, oks = [], []

    # 1. AIGC 法定标识
    label = "AI 生成 · 经典引文经人工考据核验"
    oks.append("AIGC标识") if label in text else issues.append("缺少AIGC法定标识")

    # 2. 待主理人终审
    oks.append("终审状态") if "待主理人终审" in text else issues.append("缺少待主理人终审标记")

    # 3. 引用核验：文中每个 CLASSIC-xxx 的引文须逐字出现在文中，且 status=verified
    for cid in sorted(set(re.findall(r"CLASSIC-\d{3}", text))):
        if cid not in classics:
            issues.append(f"{cid} 不存在于台账"); continue
        row = classics[cid]
        if row["status"] != "verified":
            issues.append(f"{cid} 状态={row['status']}（非verified，不得引用）"); continue
        if row["quote"] in text:
            oks.append(f"{cid}逐字一致")
        else:
            issues.append(f"{cid} 引文未逐字出现在文中")

    # 4. 反查：文中所有引用块（> 开头的整句古语）须能在台账中找到逐字匹配
    for line in text.splitlines():
        m = re.match(r"^>\s*([一-鿿，。；：？！、“”'（）()…—]{4,})\s*$", line)
        if not m:
            continue
        q = m.group(1)
        if any(k in q for k in ("AIGC", "终审", "状态", "标识", "口径", "红线")):
            continue
        if any(q == r["quote"] or q in r["quote"] for r in classics.values()):
            oks.append("引用块可溯源")
        else:
            issues.append(f"引用块无法溯源: {q[:20]}…")

    # 5. 行动牌存在性
    for aid in sorted(set(re.findall(r"A-\d{3}", text))):
        (oks if aid in actions else issues).append(f"行动牌{aid}" + ("存在" if aid in actions else "不存在"))

    # 6. 虚构标记（仅种子稿）
    if fn.startswith("先师回信"):
        oks.append("虚构场景标记") if "虚构场景" in text else issues.append("缺少虚构场景标记")

    status = "PASS" if not issues else "FAIL"
    if issues:
        fail += 1
    report.append((fn, status, oks, issues))

print("=" * 60)
for fn, status, oks, issues in report:
    print(f"[{status}] {fn}")
    for i in issues:
        print(f"    !! {i}")
    print(f"    通过项: {', '.join(oks)}")
print("=" * 60)
print(f"共 {len(report)} 个文件，{fail} 个存在问题")
sys.exit(1 if fail else 0)
