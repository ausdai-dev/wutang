# -*- coding: utf-8 -*-
"""
修复脚本：
1. 解决全局 document.querySelectorAll('.inspo-pill') 暴力覆盖卡牌库 onclick 事件导致的错误弹窗
2. 为四大卡牌库切换按钮赋予专属 class="card-lib-pill" 及宋韵 active 视觉样式
3. 确保 switchStudioCardLibrary 能够正确更新 active 状态并展示对应卡牌库
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

def main():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. CSS 补充：专属 .card-lib-pill 样式
    css_anchor = ".view-toggle-btn.active {"
    if css_anchor not in content:
        raise RuntimeError("css_anchor not found")

    new_css = """.card-lib-pill {
  background: var(--color-surface-subtle);
  border: 1px solid var(--color-border);
  border-radius: 18px;
  padding: 6px 14px;
  font-size: 13px;
  color: var(--color-ink-light);
  cursor: pointer;
  transition: all var(--trans);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  outline: none;
}
.card-lib-pill:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
  color: var(--color-primary);
  transform: translateY(-1px);
}
.card-lib-pill.active {
  background: var(--color-gold-bg) !important;
  border-color: var(--color-gold) !important;
  color: var(--color-gold) !important;
  font-weight: 700 !important;
  box-shadow: 0 2px 8px rgba(159, 116, 48, 0.16) !important;
}

""" + css_anchor

    content = content.replace(css_anchor, new_css, 1)

    # 2. HTML 替换：把 managerCardLifeTabs 内部的 inspo-pill 换成 card-lib-pill
    old_tabs_html = """        <!-- 四大平级卡牌库导航选项卡 -->
        <div class="pill-inspirations" id="managerCardLifeTabs" style="margin:0 0 18px;display:flex;gap:8px;flex-wrap:wrap;">
          <button type="button" class="inspo-pill active" id="btnTabBase32" onclick="switchStudioCardLibrary('base32')">基础解忧牌 (32)</button>
          <button type="button" class="inspo-pill" id="btnTabPantheon" onclick="switchStudioCardLibrary('pantheon')">百八常道库 (108)</button>
          <button type="button" class="inspo-pill" id="btnTabZen96" onclick="switchStudioCardLibrary('zen96')">觉察牌画廊 (96)</button>
          <button type="button" class="inspo-pill" id="btnTabThemePacks" onclick="switchStudioCardLibrary('theme')">主题卡牌包 (6)</button>
        </div>"""

    new_tabs_html = """        <!-- 四大平级卡牌库导航选项卡 -->
        <div class="pill-inspirations" id="managerCardLifeTabs" style="margin:0 0 18px;display:flex;gap:8px;flex-wrap:wrap;">
          <button type="button" class="card-lib-pill active" id="btnTabBase32" onclick="switchStudioCardLibrary('base32')">基础解忧牌 (32)</button>
          <button type="button" class="card-lib-pill" id="btnTabPantheon" onclick="switchStudioCardLibrary('pantheon')">百八常道库 (108)</button>
          <button type="button" class="card-lib-pill" id="btnTabZen96" onclick="switchStudioCardLibrary('zen96')">觉察牌画廊 (96)</button>
          <button type="button" class="card-lib-pill" id="btnTabThemePacks" onclick="switchStudioCardLibrary('theme')">主题卡牌包 (6)</button>
        </div>"""

    if old_tabs_html not in content:
        raise RuntimeError("old_tabs_html not found")
    content = content.replace(old_tabs_html, new_tabs_html, 1)

    # 3. JS 修复：修复第 17395 行全局覆盖 inspo-pill 的 Bug
    old_inspo_binding = """    // 快捷推荐灵感药丸

    Array.prototype.forEach.call(document.querySelectorAll('.inspo-pill'), function(pill) {

      pill.onclick = function() {

        textarea.value = pill.getAttribute('data-inspo');

        textarea.dispatchEvent(new Event('input'));

        textarea.focus();

        showToast('已填入体验案例，点击「帮我理一理」即可梳理');

      };

    });"""

    new_inspo_binding = """    // 快捷推荐灵感药丸（严格限定 inspoPills 灵感药丸容器内）

    var inspoWrap = $('inspoPills');

    if (inspoWrap) {

      Array.prototype.forEach.call(inspoWrap.querySelectorAll('.inspo-pill, [data-inspo]'), function(pill) {

        pill.onclick = function() {

          var textToFill = pill.getAttribute('data-inspo');

          if (!textToFill) return;

          textarea.value = textToFill;

          textarea.dispatchEvent(new Event('input'));

          textarea.focus();

          showToast('已填入体验案例，点击「帮我理一理」即可梳理');

        };

      });

    }"""

    if old_inspo_binding not in content:
        raise RuntimeError("old_inspo_binding not found")
    content = content.replace(old_inspo_binding, new_inspo_binding, 1)

    # 4. JS 修复：switchStudioCardLibrary 内部选择器适配 card-lib-pill
    old_switch_fn = """    var tabsWrap = $('managerCardLifeTabs');
    var pills = tabsWrap ? tabsWrap.querySelectorAll('.inspo-pill') : [];
    Array.prototype.forEach.call(pills, function(p) { p.classList.remove('active'); });"""

    new_switch_fn = """    var tabsWrap = $('managerCardLifeTabs');
    var pills = tabsWrap ? tabsWrap.querySelectorAll('.card-lib-pill') : [];
    Array.prototype.forEach.call(pills, function(p) { p.classList.remove('active'); });"""

    if old_switch_fn not in content:
        raise RuntimeError("old_switch_fn not found")
    content = content.replace(old_switch_fn, new_switch_fn, 1)

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("[ok] Successfully fixed pill classes and removed violent inspo click interception!")

if __name__ == "__main__":
    main()
