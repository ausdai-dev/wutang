# -*- coding: utf-8 -*-
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl_path = os.path.join(ROOT, "frontend", "_template.html")

with open(tpl_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """    // 1. 顶栏极简三入口模式切换
    if ($('tabRelief')) $('tabRelief').onclick = function() { switchMainTab('relief'); };
    if ($('tabClient')) $('tabClient').onclick = function() { switchMainTab('relief'); };
    if ($('tabMine')) $('tabMine').onclick = function() { switchMainTab('mine'); };
    if ($('tabStudio')) $('tabStudio').onclick = function() { switchMainTab('studio'); };"""

replacement = """    // 1. 顶栏模式切换 (PRD 3.0 全量 6 大用户入口 + 1 个主理人入口)
    if ($('tabRelief')) $('tabRelief').onclick = function() { switchMainTab('relief'); };
    if ($('tabClient')) $('tabClient').onclick = function() { switchMainTab('relief'); };
    if ($('tabGrowth')) $('tabGrowth').onclick = function() { switchMainTab('growth'); };
    if ($('tabWellbeing')) $('tabWellbeing').onclick = function() { switchMainTab('wellbeing'); };
    if ($('tabPractice')) $('tabPractice').onclick = function() { switchMainTab('practice'); };
    if ($('tabCards')) $('tabCards').onclick = function() { switchMainTab('cards'); };
    if ($('tabMine')) $('tabMine').onclick = function() { switchMainTab('mine'); };
    if ($('tabStudio')) $('tabStudio').onclick = function() { switchMainTab('studio'); };"""

# Handle both CRLF and LF
if target in content:
    content = content.replace(target, replacement, 1)
    print("[✓] 成功替换 LF 目标代码")
elif target.replace("\n", "\r\n") in content:
    content = content.replace(target.replace("\n", "\r\n"), replacement.replace("\n", "\r\n"), 1)
    print("[✓] 成功替换 CRLF 目标代码")
else:
    print("[!] 未找到目标代码段")
    sys.exit(1)

with open(tpl_path, "w", encoding="utf-8") as f:
    f.write(content)

print("[✓] _template.html 更新完毕")
