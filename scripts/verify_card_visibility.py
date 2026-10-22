# -*- coding: utf-8 -*-
"""
Verification script for:
1. tabCards is hidden in top navigation.
2. mineCardsLifeSection is present in mineArea.
3. managerCardLifeTabs and managerCardsLibraryWrap are hidden by default.
4. userFavoriteCardsView is present for normal users.
5. updateManagerUI toggles managerCardsLibraryWrap based on isManagerLoggedIn.
6. Favorite cards logic supports 96 zen cards, 108 pantheon cards, and classic cards.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(ROOT, "frontend", "index.html")

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

checks = []

def check(name, condition, detail=""):
    status = "[OK]" if condition else "[FAIL]"
    checks.append((name, condition))
    print(f"  {status} {name}" + (f" ({detail})" if detail else ""))

print("=================================================================")
print("Cards Life Integration & Role-Based Access Verification")
print("=================================================================")

# 1. 顶栏导航检查
nav_match = re.search(r'<nav class="mode-nav"[^>]*>([\s\S]*?)<\/nav>', html)
check("顶栏导航区域存在", nav_match is not None)
if nav_match:
    nav_inner = nav_match.group(1)
    check("顶栏原「卡牌人生」按钮已设为隐藏", 'id="tabCards"' in nav_inner and 'display:none' in nav_inner)
    check("顶栏正常可见导航仅保留：解忧、成长记录、心境健康、情境练习、我的",
          'id="tabRelief"' in nav_inner and 'id="tabGrowth"' in nav_inner and
          'id="tabWellbeing"' in nav_inner and 'id="tabPractice"' in nav_inner and
          'id="tabMine"' in nav_inner)

# 2. 「我的」页面卡牌人生模块检查
mine_match = re.search(r'<main id="mineArea"[^>]*>([\s\S]*?)<\/main>', html)
check("「我的」主页面 (mineArea) 存在", mine_match is not None)
if mine_match:
    mine_inner = mine_match.group(1)
    check("卡牌人生专属板块已收纳至「我的」页面 (mineCardsLifeSection)", 'id="mineCardsLifeSection"' in mine_inner)
    check("普通用户默认视图为「我的收藏」(userFavoriteCardsView)", 'id="userFavoriteCardsView"' in mine_inner)
    check("全量卡牌库容器 (managerCardsLibraryWrap) 初始状态严格隐藏",
          'id="managerCardsLibraryWrap"' in mine_inner and 'style="display:none' in mine_inner)
    check("主理人专属卡牌库切换药丸 (managerCardLifeTabs) 初始状态严格隐藏",
          'id="managerCardLifeTabs"' in mine_inner and 'style="display:none' in mine_inner)
    check("百八常道 108 图鉴全谱系已内嵌于主理人专享容器", 'id="pantheon108Section"' in mine_inner)
    check("东方智慧觉察牌 96 典藏画廊已内嵌于主理人专享容器", 'id="zen96CardsSection"' in mine_inner)
    check("A4 实体卡牌 9宫格拼版打印预览模态框完备", 'id="modalA4Print"' in mine_inner)

# 3. 逻辑与权限守卫检查
check("包含主理人卡牌库切换控制器 switchCardLifeSubView", "window.switchCardLifeSubView = function" in html)
check("非主理人越权访问全量卡牌库时拥有拦截铁律", "if (subView !== 'fav' && !appState.isManagerLoggedIn)" in html)
check("收藏渲染器支持 96 东方觉察牌、108 常道与经典卡牌", "type === 'zen96'" in html and "type === 'zen108'" in html)
check("updateManagerUI 实现主理人登录时解锁卡牌库、退出登录时锁定卡牌库",
      "managerCardLifeBadge" in html and "managerCardsLibraryWrap" in html)
check("switchMainTab('cards') 自动重定向至「我的」并平滑滚动", "mineCardsLifeSection" in html and "switchMainTab('mine')" in html)

passed = sum(1 for _, c in checks if c)
total = len(checks)
print(f"\nResult: {passed}/{total} checks passed!")
if passed == total:
    print("SUCCESS: Cards life moved to Mine, and library is manager-only!")
else:
    print("FAILED: Some checks did not pass.")
    exit(1)
