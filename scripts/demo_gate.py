#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悟堂 · 黑客松演示门控（Demo Gate）
==================================

演示前 60 秒一键确认全链路就绪。六组检查：

  G1  引擎回归      本地跑 wutang_pipeline.py 五大测试套件（卡牌/风险/核验/授权/端到端）
  G2  知识库一致性  跑 sync_knowledge.py 检查模式，项目与专家团引擎零漂移
  G3  MCP 桥连通    node stdio 实测 tools/list + search_classics 真实检索
  G4  线上后端健康  GET {backend}/api/health（Render free 冷启动约 50s，已放宽超时）
  G5  线上数据冒烟  GET {backend}/api/theme_packs（仅 --full）
  G6  前端站点      GET {site}（默认 https://wutangeast.netlify.app，--no-site 跳过）

用法：
  python scripts/demo_gate.py                  # 标准门控（G1-G4 + G6 前端）
  python scripts/demo_gate.py --quick          # 只跑本地项（现场断网/弱网时）
  python scripts/demo_gate.py --full           # 追加 G5 线上数据冒烟（较慢）
  python scripts/demo_gate.py --site https://xxx.netlify.app   # 覆盖默认前端地址
  python scripts/demo_gate.py --backend https://other.onrender.com
  python scripts/demo_gate.py --engine-root "C:/path/to/wutang-relief-engine"

退出码：0 = GO；1 = NO-GO（存在 ❌ 失败项）；2 = 脚本自身错误。

演示日建议：开场前 5 分钟先访问一次线上后端完成冷启动，再跑本脚本。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER = ROOT / "mcp" / "wutang-kb-server.js"
DEFAULT_ENGINE = Path(
    "C:/Users/ausda/.workbuddy/plugins/marketplaces/my-experts/"
    "plugins/wutang-relief-team/skills/wutang-relief-engine"
)
DEFAULT_BACKEND = "https://wutang-backend.onrender.com"
DEFAULT_SITE = "https://wutangeast.netlify.app"

OK, WARN, BAD, SKIP = "✅", "⚠️", "❌", "⏭"


# ---------------------------------------------------------------- 基础工具

def record(rows, status, name, detail):
    rows.append((status, name, detail))
    return rows


def run(cmd, timeout, cwd=None):
    """跑子进程，返回 (exit_code, stdout, stderr)。超时返回 (-1, "", "TIMEOUT")。"""
    try:
        p = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, cwd=str(cwd) if cwd else None,
            encoding="utf-8", errors="replace",
        )
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError as e:
        return -2, "", f"NOT_FOUND: {e}"


def http_get_json(url, timeout):
    """GET 并解析 JSON，返回 (status_code, data_or_None, elapsed_ms, err_or_None)。"""
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "wutang-demo-gate/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", "replace")
            ms = int((time.time() - t0) * 1000)
            try:
                return r.status, json.loads(body), ms, None
            except json.JSONDecodeError:
                return r.status, body[:200], ms, None
    except urllib.error.HTTPError as e:
        return e.code, None, int((time.time() - t0) * 1000), f"HTTP {e.code}"
    except Exception as e:  # 超时 / DNS / 连接拒绝
        return None, None, int((time.time() - t0) * 1000), type(e).__name__


# ---------------------------------------------------------------- G1 引擎回归

def check_engine(engine_root: Path, rows):
    pipeline = engine_root / "scripts" / "wutang_pipeline.py"
    if not pipeline.exists():
        return record(rows, BAD, "G1 引擎回归", f"找不到 {pipeline}，用 --engine-root 指定")
    code, out, err = run([sys.executable, str(pipeline)], timeout=300)
    # 解析形如 "[1/5] 卡牌匹配回归      8/8  → ..." 的统计行
    stats = re.findall(r"\[(\d)/5\]\s*(.+?)\s+(\d+)/(\d+)", out)
    if not stats and code != 0:
        return record(rows, BAD, "G1 引擎回归", f"运行失败 exit={code}: {(err or out)[:120]}")
    fails = [f"{name.strip()} {ok}/{n}" for _, name, ok, n in stats if int(ok) != int(n)]
    if fails:
        return record(rows, BAD, "G1 引擎回归", "未全过 → " + "；".join(fails))
    summary = " ".join(f"{name.strip()} {ok}/{n}" for _, name, ok, n in stats)
    return record(rows, OK, "G1 引擎回归", summary or "通过（无统计行）")


# ---------------------------------------------------------------- G2 知识库一致性

def check_sync(rows):
    script = ROOT / "scripts" / "sync_knowledge.py"
    if not script.exists():
        return record(rows, SKIP, "G2 知识库一致性", f"缺少 {script.name}，跳过")
    code, out, err = run([sys.executable, str(script)], timeout=120)
    # 摘要行形如「摘要: ✅ 30   ⚠️ 0   ❌ 0」（多空格、无斜杠）
    m_ok = re.search(r"摘要:.*?✅\s*(\d+)", out)
    m_warn = re.search(r"摘要:.*?⚠️\s*(\d+)", out)
    m_bad = re.search(r"摘要:.*?❌\s*(\d+)", out)
    if code == 0 and m_ok and m_bad and int(m_bad.group(1)) == 0:
        warn_n = int(m_warn.group(1)) if m_warn else 0
        if warn_n == 0:
            return record(rows, OK, "G2 知识库一致性", f"{m_ok.group(1)} 项全绿，零漂移")
        return record(rows, WARN, "G2 知识库一致性",
                      f"⚠️{warn_n} 项漂移 → 修复: python scripts/sync_knowledge.py --sync")
    if m_ok and m_bad:
        return record(
            rows, BAD, "G2 知识库一致性",
            f"漂移 ❌{m_bad.group(1)} → 修复: python scripts/sync_knowledge.py --sync")
    return record(rows, BAD, "G2 知识库一致性", f"运行失败 exit={code}: {(err or out)[:120]}")


# ---------------------------------------------------------------- G3 MCP 桥

def check_mcp(rows):
    if not MCP_SERVER.exists():
        return record(rows, BAD, "G3 MCP 桥", f"找不到 {MCP_SERVER}")
    msgs = [
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                               "clientInfo": {"name": "demo-gate", "version": "1.0"}}}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
        json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": "search_classics",
                               "arguments": {"query": "内耗", "limit": 2}}}),
    ]
    # MCP over stdio：逐条写入并 flush，条间短暂间隔。
    # （一次性写完立即关 stdin 会触发 Node readline 的 EOF 竞态，丢失最后一条消息的响应）
    try:
        proc = subprocess.Popen(
            ["node", str(MCP_SERVER)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace",
        )
        for m in msgs:
            proc.stdin.write(m + "\n")
            proc.stdin.flush()
            time.sleep(0.2)
        proc.stdin.close()
        out = proc.stdout.read() or ""
        proc.wait(timeout=10)
    except Exception as e:
        return record(rows, BAD, "G3 MCP 桥", f"启动失败: {type(e).__name__} {e}")

    tools, hits = [], 0
    for line in out.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == 2 and "result" in msg:
            tools = [t["name"] for t in msg["result"].get("tools", [])]
        if msg.get("id") == 3 and "result" in msg:
            text = msg["result"]["content"][0].get("text", "")
            try:
                hits = json.loads(text).get("count", 0)
            except (json.JSONDecodeError, AttributeError):
                hits = 0
    if len(tools) >= 6 and hits > 0:
        return record(rows, OK, "G3 MCP 桥", f"{len(tools)} 工具就绪，检索「内耗」命中 {hits} 条")
    if not tools:
        return record(rows, BAD, "G3 MCP 桥", "tools/list 无响应，检查 node 与脚本")
    return record(rows, WARN, "G3 MCP 桥", f"{len(tools)} 工具在列但检索命中 {hits} 条")


# ---------------------------------------------------------------- G4/G5 线上

def check_backend_health(backend: str, rows):
    st, data, ms, err = http_get_json(backend.rstrip("/") + "/api/health", timeout=60)
    if err:
        hint = "（Render free 冷启动约 50s，提前 5 分钟访问一次预热）" if err == "timeout" else ""
        return record(rows, BAD, "G4 线上后端健康", f"{err} {hint}")
    if st == 200:
        return record(rows, OK, "G4 线上后端健康", f"200 · {ms}ms")
    return record(rows, BAD, "G4 线上后端健康", f"HTTP {st}")


def check_backend_data(backend: str, rows):
    st, data, ms, err = http_get_json(backend.rstrip("/") + "/api/theme_packs", timeout=60)
    if err:
        return record(rows, BAD, "G5 线上数据冒烟", f"{err}（冷启动中？重试或稍后再跑）")
    if st == 200 and data:
        n = len(data) if isinstance(data, (list, dict)) else 1
        return record(rows, OK, "G5 线上数据冒烟", f"200 · {n} 个主题包 · {ms}ms")
    return record(rows, WARN, "G5 线上数据冒烟", f"HTTP {st} 或空响应")


def check_frontend(site: str, rows):
    if not site:
        return record(rows, SKIP, "G6 前端站点", "未传 --site，跳过（传入 Netlify 地址可检查）")
    st, _, ms, err = http_get_json(site.rstrip("/"), timeout=30)
    if err:
        return record(rows, BAD, "G6 前端站点", f"{err}")
    if st == 200:
        return record(rows, OK, "G6 前端站点", f"200 · {ms}ms")
    return record(rows, WARN, "G6 前端站点", f"HTTP {st}")


# ---------------------------------------------------------------- 主流程

def main():
    ap = argparse.ArgumentParser(description="悟堂 · 黑客松演示门控")
    ap.add_argument("--quick", action="store_true", help="只跑本地项 G1-G3")
    ap.add_argument("--full", action="store_true", help="追加 G5 线上数据冒烟")
    ap.add_argument("--backend", default=DEFAULT_BACKEND, help="Render 后端地址")
    ap.add_argument("--site", default=DEFAULT_SITE, help="Netlify 前端地址")
    ap.add_argument("--no-site", action="store_true", help="跳过 G6 前端站点检查")
    ap.add_argument("--engine-root", default=str(DEFAULT_ENGINE), help="专家团引擎目录")
    args = ap.parse_args()

    engine_root = Path(args.engine_root)
    rows = []

    print("=" * 64)
    print(" 悟堂 · 黑客松演示门控  Demo Gate")
    print(f" 后端: {args.backend}")
    print("=" * 64)

    t0 = time.time()
    check_engine(engine_root, rows)
    check_sync(rows)
    check_mcp(rows)
    if not args.quick:
        check_backend_health(args.backend, rows)
        if args.full:
            check_backend_data(args.backend, rows)
    else:
        record(rows, SKIP, "G4 线上后端健康", "--quick 模式跳过")
        record(rows, SKIP, "G5 线上数据冒烟", "--quick 模式跳过")
    site = "" if args.no_site else args.site
    check_frontend(site, rows)

    for status, name, detail in rows:
        print(f"  {status}  {name:<14} {detail}")

    n_bad = sum(1 for s, _, _ in rows if s == BAD)
    n_warn = sum(1 for s, _, _ in rows if s == WARN)
    n_skip = sum(1 for s, _, _ in rows if s == SKIP)
    elapsed = int(time.time() - t0)

    print("-" * 64)
    if n_bad:
        print(f" 结论: NO-GO ❌  {n_bad} 项失败（{n_warn} 警告 / {n_skip} 跳过）· 耗时 {elapsed}s")
        print(" 修复建议: 按上方 ❌ 行的命令逐项处理；仍失败先跑 G1/G2 定位本地问题。")
        sys.exit(1)
    verdict = "GO ✅" if n_warn == 0 else "GO（有警告）⚠️"
    print(f" 结论: {verdict}  0 失败 · {n_warn} 警告 / {n_skip} 跳过 · 耗时 {elapsed}s")
    if n_skip:
        print(" 提示: 加 --full 与 --site <netlify地址> 可覆盖全部六组检查。")
    sys.exit(0)


if __name__ == "__main__":
    main()
