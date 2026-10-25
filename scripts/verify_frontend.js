#!/usr/bin/env node
/**
 * 悟堂前端交互回归测试（jsdom）
 * ---------------------------------------------------------------------------
 * 为什么需要这个脚本：
 *   前端是单文件内联 HTML，改动后只能靠浏览器点。本机 agent-browser 不可靠
 *   （`open` 会长时间挂起），所以用 jsdom 做无头 DOM 级验证。
 *
 *   它能抓到静态检查抓不到的一类 bug ——「代码写了，但和 CSS / 选择器对不上」。
 *   例：2026-10-16 修的「点击翻开这张牌」无反应，根因是
 *       CSS 用 `.awareness-card-container.is-flipped`，JS 却 `classList.add('flipped')`，
 *       类名差一个 `is-` 前缀，卡片永远不会翻转。
 *
 * 运行：
 *   NODE_PATH="C:/Users/ausda/.workbuddy-ai/binaries/node/workspace/node_modules" \
 *   "C:/Users/ausda/.workbuddy-ai/binaries/node/versions/22.22.2-6/node.exe" \
 *   scripts/verify_frontend.js
 *
 * 前置：jsdom（已装在 node workspace）
 *   cd C:/Users/ausda/.workbuddy-ai/binaries/node/workspace && npm install jsdom
 */
'use strict';

const fs = require('fs');
const path = require('path');

let JSDOM, VirtualConsole;
try {
  ({ JSDOM, VirtualConsole } = require('jsdom'));
} catch (e) {
  ({ JSDOM, VirtualConsole } = require(
    'C:/Users/ausda/.workbuddy-ai/binaries/node/workspace/node_modules/jsdom'));
}

const ROOT = path.resolve(__dirname, '..');
const HTML_PATH = path.join(ROOT, 'frontend', 'index.html');
const html = fs.readFileSync(HTML_PATH, 'utf8');

const errors = [];
const vc = new VirtualConsole();
vc.on('jsdomError', (e) => errors.push(e.message || String(e)));
vc.on('error', (...a) => errors.push(a.join(' ')));

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  virtualConsole: vc,
});
const { window } = dom;
const doc = window.document;

const results = [];
const check = (name, cond, extra) => {
  results.push({ name, pass: !!cond });
  console.log(`  ${cond ? 'PASS' : 'FAIL'}  ${name}${extra ? '   ' + extra : ''}`);
};
const visible = (id) => {
  const n = doc.getElementById(id);
  return !!n && !n.classList.contains('hidden');
};

setTimeout(() => {
  console.log('=== 0. 页面脚本错误 ===');
  if (errors.length) {
    errors.slice(0, 8).forEach((e) => console.log('  ' + e));
  } else {
    console.log('  无');
  }
  check('页面初始化无 JS 错误', errors.length === 0);

  // ---------------- A. 成长页签中的心事与觉察入口 ----------------
  console.log('\n=== A. 成长页签入口迁移 ===');
  const growthTab = doc.getElementById('tabGrowth');
  const growthArea = doc.getElementById('growthArea');
  const growthMount = doc.getElementById('growthEntryMount');
  const entrySwitchBar = doc.querySelector('.entry-switch-bar');
  const scenarioSection = doc.getElementById('scenarioSection');
  const directArea = doc.getElementById('entryDirectArea');
  const cardArea = doc.getElementById('entryCardArea');
  check('心事与觉察入口已挂载在成长页签',
    !!growthMount && [entrySwitchBar, scenarioSection, directArea, cardArea].every((node) => node && node.parentElement === growthMount));
  check('解忧页签不再承载双入口内容',
    !doc.querySelector('#clientArea .entry-switch-bar') && !doc.querySelector('#clientArea #entryDirectArea') && !doc.querySelector('#clientArea #entryCardArea'));
  if (growthTab) growthTab.click();
  check('点击成长页签显示入口', growthArea && !growthArea.classList.contains('hidden') && !growthMount.classList.contains('hidden'));
  const growthEntryBtnDirect = doc.getElementById('entryBtnDirect');
  const growthEntryBtnCard = doc.getElementById('entryBtnCard');
  check('心事与觉察两个按钮仍存在', !!growthEntryBtnDirect && !!growthEntryBtnCard);
  if (growthEntryBtnCard) growthEntryBtnCard.click();
  check('成长页签可切换到觉察牌', !cardArea.classList.contains('hidden') && directArea.classList.contains('hidden'));
  if (growthEntryBtnDirect) growthEntryBtnDirect.click();
  check('成长页签可切回写心事', !directArea.classList.contains('hidden') && cardArea.classList.contains('hidden'));
  const tabRelief = doc.getElementById('tabRelief');
  if (tabRelief) tabRelief.click();
  check('切回解忧页签时成长入口隐藏', growthArea.classList.contains('hidden'));

  // ---------------- B. 今日觉察牌：翻转交互 ----------------
  console.log('\n=== B. 今日觉察牌翻转 ===');
  const entryBtnCard = doc.getElementById('entryBtnCard');
  const box = doc.getElementById('awarenessCardBox');
  const flipBtn = doc.querySelector('.card-back-flip-btn');

  check('抽卡入口与卡片容器存在', !!entryBtnCard && !!box);
  check('「点击翻开这张牌」元素存在', !!flipBtn);
  if (entryBtnCard) entryBtnCard.click();
  check('抽卡区可见', visible('entryCardArea'));

  if (box && flipBtn) {
    check('点击前未翻转', !box.classList.contains('is-flipped'));
    flipBtn.click();
    check('点击后已翻转 (is-flipped)', box.classList.contains('is-flipped'),
      `class="${box.className}"`);

    const followup = doc.getElementById('awFollowupBox');
    const proceed = doc.getElementById('awProceedWrap');
    doc.getElementById('btnAwResonates').click();
    check('「很像我」显示深入觉察框', !followup.classList.contains('hidden'));
    check('「很像我」显示继续按钮', !proceed.classList.contains('hidden'));

    doc.getElementById('btnAwChange').click();
    check('「换一张」立即翻回', !box.classList.contains('is-flipped'));
  }

  setTimeout(() => {
    if (box) check('「换一张」250ms 后翻开新牌', box.classList.contains('is-flipped'));

    const cancel = doc.getElementById('btnAwCancel');
    if (cancel) {
      cancel.click();
      check('「先不继续」回到直接输入区', visible('entryDirectArea'));
    }

    // ---------------- B. 主流程：输入 -> 四步 -> 卡片 ----------------
    console.log('\n=== B. 主流程 ===');
    const ta = doc.getElementById('userTextarea');
    const btn = doc.getElementById('btnSubmitClient');
    check('提交按钮初始禁用', btn.hasAttribute('disabled'));

    ta.value = '最近工作上总被否定，我开始怀疑是不是自己真的不行。';
    ta.dispatchEvent(new window.Event('input'));
    check('输入后提交按钮启用', !btn.hasAttribute('disabled'));

    btn.click();
    setTimeout(() => {
      check('提交后进入结果视图', visible('userResult'),
        ['userHome', 'userLoading', 'userResult', 'userSafety', 'userCard'].filter(visible).join(','));

      const four = doc.getElementById('fourStepList');
      check('四步内容非空', four && (four.textContent || '').trim().length > 50,
        four ? `${(four.textContent || '').trim().length} 字符` : '');
      check('四步含经典引用块', !!doc.querySelector('.classic-quote-text'),
        (doc.querySelector('.classic-quote-text') || {}).textContent || '');

      const cardBtn = doc.getElementById('btnGenerateCard');
      if (cardBtn) {
        cardBtn.click();
        check('生成解忧笺进入卡片视图', visible('userCard'));
        const ct = doc.getElementById('cardTheme');
        const cq = doc.getElementById('cardQuote');
        check('卡片主题词非空', ct && (ct.textContent || '').trim().length > 0,
          ct ? `"${ct.textContent}"` : '');
        check('卡片引用非空', cq && (cq.textContent || '').trim().length > 0);
      }

      // ---------------- C. 阅读字体切换（宋刻本 / 文楷 / 黑体） ----------------
      console.log('\n=== C. 阅读字体切换 ===');
      const htmlEl = doc.documentElement;
      const fontBtn = doc.getElementById('btnFontToggle');
      const fontPanel = doc.getElementById('fontPanel');
      const fontList = doc.getElementById('fontOptionList');
      check('字体切换按钮与面板存在', !!fontBtn && !!fontPanel && !!fontList);
      check('默认字体为宋刻本(songke)', htmlEl.getAttribute('data-font') === 'songke',
        htmlEl.getAttribute('data-font'));
      check('字体面板默认隐藏', fontPanel && !fontPanel.classList.contains('show'));
      check('渲染 4 个字体选项', fontList && fontList.querySelectorAll('.font-option').length === 4,
        fontList ? fontList.querySelectorAll('.font-option').length + ' 个' : '无');

      if (fontBtn) fontBtn.click();
      check('点击按钮后面板展开', fontPanel && fontPanel.classList.contains('show'));

      const songkeOpt = doc.querySelector('.font-option[data-font-id="songke"]');
      check('宋刻本选项存在', !!songkeOpt);
      if (songkeOpt) songkeOpt.click();
      check('选择宋刻本后 data-font=songke', htmlEl.getAttribute('data-font') === 'songke');
      // jsdom 不解析 var() 间接引用：--font-serif 为 var(--font-songke)，需再查预设变量本身
      check('CSS 变量 --font-serif 指向宋刻本预设',
        window.getComputedStyle(htmlEl).getPropertyValue('--font-serif').indexOf('var(--font-songke)') > -1,
        window.getComputedStyle(htmlEl).getPropertyValue('--font-serif'));
      check('宋刻本预设变量含 KingHwa_OldSong',
        window.getComputedStyle(htmlEl).getPropertyValue('--font-songke').indexOf('KingHwa_OldSong') > -1,
        window.getComputedStyle(htmlEl).getPropertyValue('--font-songke'));
      const fontLabel = doc.getElementById('fontCurrentLabel');
      check('按钮标签更新为宋刻本', fontLabel && fontLabel.textContent === '宋刻本');
      check('选择后面板自动收起', fontPanel && !fontPanel.classList.contains('show'));
      check('宋刻本选项高亮',
        !!doc.querySelector('.font-option[data-font-id="songke"].active'));
      // 预览字形 style 属性须完整（防 family 引号截断属性这类 bug）
      const previewStyle = (doc.querySelector('.font-option[data-font-id="songke"] .font-option-preview') || {}).style;
      check('宋刻本预览字形内联样式完整',
        !!previewStyle && previewStyle.fontFamily.indexOf('KingHwa_OldSong') > -1,
        previewStyle ? previewStyle.fontFamily : '无');

      // 面板开关：再展开 -> 点击页面其他处收起
      if (fontBtn) fontBtn.click();
      check('再次点击可重新展开面板', fontPanel && fontPanel.classList.contains('show'));
      doc.body.click();
      check('点击页面其他后面板收起', fontPanel && !fontPanel.classList.contains('show'));

      // 切换其余预设并回到默认
      const pickFont = (id) => {
        const el = doc.querySelector('.font-option[data-font-id="' + id + '"]');
        if (el) el.click();
      };
      pickFont('kai');
      check('可切换到霞鹜文楷(kai)', htmlEl.getAttribute('data-font') === 'kai');
      check('文楷预设覆写 --font-serif',
        window.getComputedStyle(htmlEl).getPropertyValue('--font-serif').indexOf('var(--font-kai)') > -1);
      check('文楷预设变量含 LXGW WenKai',
        window.getComputedStyle(htmlEl).getPropertyValue('--font-kai').indexOf('LXGW WenKai') > -1);
      pickFont('hei');
      check('可切换到思源黑体(hei)', htmlEl.getAttribute('data-font') === 'hei');
      check('黑体预设覆写 --font-sans',
        window.getComputedStyle(htmlEl).getPropertyValue('--font-sans').indexOf('var(--font-hei)') > -1);
      check('黑体预设变量含 Noto Sans SC',
        window.getComputedStyle(htmlEl).getPropertyValue('--font-hei').indexOf('Noto Sans SC') > -1);
      pickFont('song');
      check('可切回思源宋体(song)', htmlEl.getAttribute('data-font') === 'song');

      // ---------------- D. 字体偏好持久化恢复 ----------------
      // 主 DOM 为 opaque origin（localStorage 不可用，应用已 try/catch 兜底）；
      // 此处用带 localStorage 垫片的第二个 DOM 实例验证「刷新后恢复上次字体」链路。
      console.log('\n=== D. 字体偏好持久化恢复 ===');
      const fontStore = { wutang_font_pref: 'songke' };
      const dom2 = new JSDOM(html, {
        runScripts: 'dangerously',
        pretendToBeVisual: true,
        beforeParse(w2) {
          Object.defineProperty(w2, 'localStorage', {
            configurable: true,
            value: {
              getItem: (k) => (k in fontStore ? fontStore[k] : null),
              setItem: (k, v) => { fontStore[k] = String(v); },
              removeItem: (k) => { delete fontStore[k]; },
              clear: () => { Object.keys(fontStore).forEach((k) => delete fontStore[k]); }
            }
          });
        }
      });
      setTimeout(async () => {
        const doc2 = dom2.window.document;
        check('刷新后恢复上次字体偏好(songke)',
          doc2.documentElement.getAttribute('data-font') === 'songke',
          doc2.documentElement.getAttribute('data-font'));
        const label2 = doc2.getElementById('fontCurrentLabel');
        check('恢复后按钮标签为宋刻本', label2 && label2.textContent === '宋刻本');
        check('恢复后宋刻本选项高亮',
          !!doc2.querySelector('.font-option[data-font-id="songke"].active'));

        // 使用真实 origin 覆盖无偏好、无效偏好和所有合法偏好的刷新恢复。
        await Promise.all([null, 'invalid-font', 'songke', 'song', 'kai', 'hei'].map(async (saved) => {
          const makeDom = (value) => new JSDOM(html, {
            url: 'https://font-test.invalid/',
            runScripts: 'dangerously',
            pretendToBeVisual: true,
            virtualConsole: new VirtualConsole(),
            beforeParse(w) {
              if (value !== null) w.localStorage.setItem('wutang_font_pref', value);
            }
          });
          const instance = makeDom(saved);
          const w = instance.window;
          const expected = ['songke', 'song', 'kai', 'hei'].includes(saved) ? saved : 'songke';
          check('首屏立即恢复字体(' + saved + ')',
            w.document.documentElement.getAttribute('data-font') === expected);
          await new Promise((resolve) => w.addEventListener('load', resolve, { once: true }));
          check('初始化后保持字体(' + saved + ')',
            w.document.documentElement.getAttribute('data-font') === expected);
          const target = expected === 'hei' ? 'kai' : 'hei';
          w.document.querySelector('.font-option[data-font-id="' + target + '"]').click();
          check('手动选择写入持久化(' + saved + ')',
            w.localStorage.getItem('wutang_font_pref') === target);
          // 模拟字体样式异步加载完成或失败，不应覆盖用户后续选择。
          w.document.querySelectorAll('link[rel="stylesheet"]').forEach((link) => {
            link.dispatchEvent(new w.Event('load'));
            link.dispatchEvent(new w.Event('error'));
          });
          await new Promise((resolve) => w.setTimeout(resolve, 100));
          check('异步字体事件后保持选择(' + saved + ')',
            w.document.documentElement.getAttribute('data-font') === target);
          const refreshed = makeDom(w.localStorage.getItem('wutang_font_pref'));
          await new Promise((resolve) => refreshed.window.addEventListener('load', resolve, { once: true }));
          check('刷新保持手动选择(' + saved + ')',
            refreshed.window.document.documentElement.getAttribute('data-font') === target);
          refreshed.window.close();
          w.close();
        }));
        check('宋刻本回退链不含思源宋体',
          !window.getComputedStyle(htmlEl).getPropertyValue('--font-songke').includes('Noto Serif'));
        dom2.window.close();

        // ---------------- E. 心境专区三药丸导航 ----------------
        console.log('\n=== E. 心境专区三药丸导航 ===');
        const tabWellbeing = doc.getElementById('tabWellbeing');
        if (tabWellbeing) tabWellbeing.click();
        const wellbeingArea = doc.getElementById('wellbeingArea');
        check('点击心境页签显示心境专区', wellbeingArea && !wellbeingArea.classList.contains('hidden'));

        const wbBtnSleep = doc.getElementById('wbBtnSleep');
        const wbBtnAssessment = doc.getElementById('wbBtnAssessment');
        const wbBtnResources = doc.getElementById('wbBtnResources');
        check('心境药丸导航三个按钮均存在', !!wbBtnSleep && !!wbBtnAssessment && !!wbBtnResources);

        const sleepSec = doc.getElementById('sleepHomeSection');
        const assessSec = doc.getElementById('wellbeingAssessmentSection');
        const resSec = doc.getElementById('wellbeingResourcesSection');
        check('心境三大并列功能容器均存在', !!sleepSec && !!assessSec && !!resSec);

        check('默认激活今夜安歇药丸', wbBtnSleep.classList.contains('active') && !sleepSec.classList.contains('hidden'));
        check('自评与资源容器默认隐藏', assessSec.classList.contains('hidden') && resSec.classList.contains('hidden'));

        wbBtnAssessment.click();
        check('点击切换到心理自评药丸', wbBtnAssessment.classList.contains('active') && !wbBtnSleep.classList.contains('active'));
        check('心理自评容器显示且安歇/资源隐藏', !assessSec.classList.contains('hidden') && sleepSec.classList.contains('hidden') && resSec.classList.contains('hidden'));

        wbBtnResources.click();
        check('点击切换到资源导航药丸', wbBtnResources.classList.contains('active') && !wbBtnAssessment.classList.contains('active'));
        check('资源导航容器显示且安歇/自评隐藏', !resSec.classList.contains('hidden') && sleepSec.classList.contains('hidden') && assessSec.classList.contains('hidden'));
        const resPanel = doc.getElementById('resourcePanel');
        check('切换到资源导航自动展开资源面板', resPanel && !resPanel.classList.contains('hidden'));

        wbBtnAssessment.click();
        const toResLink = doc.getElementById('pss10ToResourcesLink');
        check('自评报告中资源导航跳转链接存在', !!toResLink);
        if (toResLink) toResLink.click();
        check('点击报告内转介链接跳转至资源导航药丸', wbBtnResources.classList.contains('active') && !resSec.classList.contains('hidden') && assessSec.classList.contains('hidden'));

        wbBtnSleep.click();
        check('点击切回今夜安歇药丸', wbBtnSleep.classList.contains('active') && !sleepSec.classList.contains('hidden') && resSec.classList.contains('hidden'));

        // ---------------- F. 先贤 @ 提及功能测试 ----------------
        console.log('\n=== F. 先贤 @ 提及与特定人唤起 ===');
        const chatInput = doc.getElementById('chatInput');
        const btnChatAt = doc.getElementById('btnChatAt');
        const chatMentionMenu = doc.getElementById('chatMentionMenu');
        check('聊天输入框与 @ 触发按钮均存在', !!chatInput && !!btnChatAt && !!chatMentionMenu);
        check('@ 候选菜单初始隐藏', chatMentionMenu.classList.contains('hidden'));

        // 点击 @ 按钮测试
        btnChatAt.click();
        check('点击 @ 按钮后展开候选菜单', !chatMentionMenu.classList.contains('hidden'));
        const candItems = chatMentionMenu.querySelectorAll('.chat-mention-item');
        check('候选菜单中包含先贤候选项', candItems.length >= 10);

        // 键入 @ 过滤测试
        chatInput.value = '@su';
        chatInput.selectionStart = chatInput.selectionEnd = 3;
        chatInput.dispatchEvent(new window.Event('input', { bubbles: true }));
        const filteredItems = chatMentionMenu.querySelectorAll('.chat-mention-item');
        check('输入 @su 能够过滤出苏轼候选项', filteredItems.length > 0 && filteredItems[0].textContent.includes('苏轼'));

        // 键盘 Enter 补全选择
        const enterEvt = new window.KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true });
        chatInput.dispatchEvent(enterEvt);
        check('Enter 确认选择后自动补全为 @苏轼 ', chatInput.value.includes('@苏轼 '));
        check('补全后候选菜单自动收起', chatMentionMenu.classList.contains('hidden'));

        console.log('\n=== 汇总 ===');
        const failed = results.filter((r) => !r.pass);
        console.log(`  ${results.length - failed.length}/${results.length} 通过`);
        if (failed.length) {
          failed.forEach((f) => console.log('  失败: ' + f.name));
          console.log('\n存在失败项');
          process.exit(1);
        }
        console.log('\n全部通过');
        process.exit(0);
      }, 1500);
    }, 2200);
  }, 500);
}, 600);
