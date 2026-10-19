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

  // ---------------- A. 今日觉察牌：翻转交互 ----------------
  console.log('\n=== A. 今日觉察牌翻转 ===');
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
    }, 2200);
  }, 500);
}, 600);
