# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 知识库同步与漂移检查 (sync_knowledge)

背景：同一份知识在三处存在，任何一处手动改动都会造成漂移：
  1) 项目 knowledge/                                  ← 唯一事实源 (SSoT)
  2) 专家团引擎 wutang-relief-engine/knowledge/ 与 frontend/assets/
  3) 项目 frontend/assets/ 与 frontend/index.html      ← 构建产物

同步方向固定为「项目 → 引擎」：
  --check      只检查漂移并输出报告（默认模式，零写入）
  --sync       执行同步；覆盖引擎侧文件前自动备份为 <文件名>.bak-YYYYMMDD
  --dry-run    配合 --sync 使用，只打印将执行的动作，不落盘
  --engine-root PATH  覆盖引擎目录（默认指向本机专家团插件）

用法：
  python scripts/sync_knowledge.py
  python scripts/sync_knowledge.py --sync
  python scripts/sync_knowledge.py --sync --dry-run
"""

import argparse
import csv
import datetime
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_ENGINE_ROOT = (
    Path(os.path.expanduser("~"))
    / ".workbuddy" / "plugins" / "marketplaces" / "my-experts" / "plugins"
    / "wutang-relief-team" / "skills" / "wutang-relief-engine"
)

SCRIPT_FILES = ["build_knowledge.py", "build_frontend.py", "wutang_pipeline.py"]
KNOWLEDGE_FILES = [
    "classics.csv", "source_index.md",
    "cards_action.json", "cards_mindset.json", "cards_wisdom.json",
    "brand_tone.md", "safety_rules.md",
]
ASSET_FILES = ["classics.json", "wutang-data.json"]
TEST_CASE_FILES = [
    "card_matching_cases.json", "citation_cases.csv", "consent_cases.csv",
    "safety_cases.csv", "synthetic_normal_cases.csv", "synthetic_normal_cases.json",
]
CORPUS_FILES = [
    "__init__.py", "existing_by_cat.json",
    "part1_cultivation.py", "part2_emotion.py", "part3_conduct.py",
    "part4_relation.py", "part5_choice.py", "part6_adversity.py",
    "part7_negative.py",
]

OK, WARN, BAD, SKIP = "✅", "⚠️", "❌", "➖"


def md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def describe(path: Path) -> str:
    """给人看的一列摘要：JSON 列表报条数，CSV 报行数，其它报字节数。"""
    try:
        if path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return f"{len(data)} 条"
            return f"{len(data)} 键"
        if path.suffix == ".csv":
            with open(path, encoding="utf-8-sig") as f:
                return f"{sum(1 for _ in csv.reader(f)) - 1} 行"
        return f"{path.stat().st_size:,} B"
    except Exception as exc:  # 描述失败不影响主流程
        return f"解析失败({exc.__class__.__name__})"


def check_group(title: str, proj_rel: str, eng_rel: str, files, engine_root: Path):
    """对比一组文件，返回 (rows, drift_files, missing_files)。"""
    rows, drift, missing = [], [], []
    print(f"\n[{title}]  {proj_rel}  ↔  引擎 {eng_rel}")
    for name in files:
        p = ROOT / proj_rel / name
        e = engine_root / eng_rel / name
        if not p.exists():
            rows.append((BAD, name, "项目侧缺失", ""))
            continue
        if not e.exists():
            rows.append((WARN, name, describe(p), "引擎缺失，同步时将创建"))
            missing.append(name)
            continue
        same = md5(p) == md5(e)
        detail = describe(p)
        if same:
            rows.append((OK, name, detail, "一致"))
        else:
            eng_detail = describe(e)
            rows.append((WARN, name, f"项目 {detail} / 引擎 {eng_detail}", "不一致"))
            drift.append(name)
    for status, name, detail, note in rows:
        print(f"  {status} {name:<24} {detail:<28} {note}")
    return rows, drift, missing


def check_frontend_freshness():
    """构建产物新鲜度：语料/脚本更新后，assets 与 index.html 是否落后。"""
    rows = []

    def newest(paths):
        mtimes = [p.stat().st_mtime for p in paths if p.exists()]
        return max(mtimes) if mtimes else 0

    corpus = [p for p in (ROOT / "scripts" / "knowledge_corpus").glob("*") if p.is_file()]
    kb_src = [ROOT / "scripts" / "build_knowledge.py"] + corpus
    src_time = newest(kb_src)
    print("\n[前端资产新鲜度]  frontend/assets/  是否由最新语料生成")
    for name in ASSET_FILES:
        a = ROOT / "frontend" / "assets" / name
        if not a.exists():
            rows.append((BAD, name, "缺失", ""))
        elif a.stat().st_mtime < src_time:
            rows.append((WARN, name, "落后于语料源", "建议运行 python scripts/build_knowledge.py"))
        else:
            rows.append((OK, name, "为最新生成产物", ""))
        print(f"  {rows[-1][0]} {name:<24} {rows[-1][2]:<28} {rows[-1][3]}")

    fe_src = [
        ROOT / "frontend" / "_template.html",
        ROOT / "frontend" / "assets" / "classics.json",
        ROOT / "frontend" / "assets" / "wutang-data.json",
    ] + [ROOT / "knowledge" / n for n in
         ("cards_mindset.json", "cards_wisdom.json", "cards_action.json",
          "theme_packs.json", "practice_scenarios.json")]
    fe_time = newest(fe_src)
    idx = ROOT / "frontend" / "index.html"
    print("\n[前端页面新鲜度]  frontend/index.html")
    if not idx.exists():
        rows.append((BAD, "index.html", "缺失", "运行 python scripts/build_frontend.py"))
    elif idx.stat().st_mtime < fe_time:
        rows.append((WARN, "index.html", "落后于输入", "运行 python scripts/build_frontend.py"))
    else:
        rows.append((OK, "index.html", "为最新构建产物", ""))
    print(f"  {rows[-1][0]} {'index.html':<24} {rows[-1][2]:<28} {rows[-1][3]}")
    return rows


def run_checks(engine_root: Path):
    all_rows = []
    print("\n[语料源 SSoT]  scripts/knowledge_corpus/  ↔  引擎 knowledge_corpus/")
    corpus_drift = []
    for name in CORPUS_FILES:
        p = ROOT / "scripts" / "knowledge_corpus" / name
        e = engine_root / "scripts" / "knowledge_corpus" / name
        if not e.exists():
            print(f"  {WARN} {name:<24} {'引擎缺失':<28} 语料源以人工裁决为准")
            all_rows.append((WARN, name))
            continue
        if md5(p) == md5(e):
            print(f"  {OK} {name:<24} {'一致':<28} 只读检查，不自动同步")
            all_rows.append((OK, name))
        else:
            print(f"  {WARN} {name:<24} {'不一致':<28} 语料源分歧，请人工裁决方向")
            corpus_drift.append(name)
            all_rows.append((WARN, name))

    r1, d1, m1 = check_group("构建脚本", "scripts", "scripts", SCRIPT_FILES, engine_root)
    r2, d2, m2 = check_group("知识文件", "knowledge", "knowledge", KNOWLEDGE_FILES, engine_root)
    r3, d3, m3 = check_group("前端资产", "frontend/assets", "frontend/assets", ASSET_FILES, engine_root)
    r5, d5, m5 = check_group("测试用例", "test_cases", "test_cases", TEST_CASE_FILES, engine_root)
    all_rows += [(s, n) for s, n, _, _ in r1 + r2 + r3 + r5]
    r4 = check_frontend_freshness()
    all_rows += [(s, n) for s, n, _, _ in r4]

    groups = [
        ("构建脚本", "scripts", "scripts", SCRIPT_FILES, d1 + m1),
        ("知识文件", "knowledge", "knowledge", KNOWLEDGE_FILES, d2 + m2),
        ("前端资产", "frontend/assets", "frontend/assets", ASSET_FILES, d3 + m3),
        ("测试用例", "test_cases", "test_cases", TEST_CASE_FILES, d5 + m5),
    ]

    counts = {OK: 0, WARN: 0, BAD: 0}
    for status, _ in all_rows:
        counts[status] = counts.get(status, 0) + 1
    print(f"\n摘要: {OK} {counts[OK]}   {WARN} {counts[WARN]}   {BAD} {counts[BAD]}")
    if corpus_drift:
        print(f"{WARN} 语料源存在分歧({len(corpus_drift)} 个文件)，同步仅复制构建产物，不覆盖引擎语料源码。")
    if counts[WARN] or counts[BAD]:
        print("提示: 执行 python scripts/sync_knowledge.py --sync 以项目为准对齐引擎（自动备份）。")
    return counts, corpus_drift, groups


def do_sync(engine_root: Path, dry_run: bool):
    today = datetime.date.today().strftime("%Y%m%d")
    print(f"同步方向: 项目 → 引擎\n引擎目录: {engine_root}")
    if dry_run:
        print("(dry-run：只打印动作，不写文件)\n")

    _, _, groups = run_checks(engine_root)
    targets = []
    for group_name, proj_rel, eng_rel, files, changed in groups:
        for name in changed:
            targets.append((group_name, ROOT / proj_rel / name, engine_root / eng_rel / name))

    if not targets:
        print("\n没有需要同步的文件（已全部一致）。")
        return 0

    print(f"\n待同步 {len(targets)} 个文件:")
    ok_count = 0
    for group_name, src, dst in targets:
        rel = dst.relative_to(engine_root)
        if dry_run:
            print(f"  {OK} [{group_name}] {src.name}  →  引擎 {rel}（将先备份）")
            ok_count += 1
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                bak = dst.with_name(f"{dst.name}.bak-{today}")
                shutil.copy2(dst, bak)
                print(f"  {OK} [{group_name}] 备份 {rel} → {bak.name}")
            shutil.copy2(src, dst)
            print(f"  {OK} [{group_name}] 已同步 {src.name} → 引擎 {rel}")
            ok_count += 1
        except Exception as exc:
            print(f"  {BAD} [{group_name}] {src.name} 同步失败: {exc}")

    if dry_run:
        print(f"\ndry-run 完成：{ok_count} 个文件待同步。去掉 --dry-run 执行实际同步。")
        return 0
    print(f"\n同步完成：{ok_count}/{len(targets)} 个文件。以下为同步后复查:\n")
    run_checks(engine_root)
    return 0 if ok_count == len(targets) else 2


def main():
    parser = argparse.ArgumentParser(description="悟堂知识库漂移检查与同步（项目 → 引擎）")
    parser.add_argument("--check", action="store_true", help="只检查漂移（默认）")
    parser.add_argument("--sync", action="store_true", help="执行同步（覆盖前自动备份 .bak-日期）")
    parser.add_argument("--dry-run", action="store_true", help="配合 --sync，只打印动作")
    parser.add_argument("--engine-root", default=str(DEFAULT_ENGINE_ROOT), help="引擎目录路径")
    args = parser.parse_args()

    engine_root = Path(args.engine_root)
    if not engine_root.exists():
        print(f"{BAD} 引擎目录不存在: {engine_root}")
        print("    请用 --engine-root 指定 wutang-relief-engine 目录。")
        return 2

    print("=" * 62)
    print(" 悟堂 · 知识库漂移检查与同步   SSoT = 项目 knowledge/")
    print("=" * 62)

    if args.sync:
        return do_sync(engine_root, args.dry_run)
    counts, _, _ = run_checks(engine_root)
    return 0 if not (counts[WARN] or counts[BAD]) else 1


if __name__ == "__main__":
    sys.exit(main())
