const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

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
window.scrollTo = () => {};
const doc = window.document;

setTimeout(() => {
  const tabTests = [
    { tabId: 'tabGrowth', areaId: 'growthArea', name: '成长记录' },
    { tabId: 'tabWellbeing', areaId: 'wellbeingArea', name: '心境健康' },
    { tabId: 'tabPractice', areaId: 'practiceArea', name: '情境练习' },
    { tabId: 'tabCards', areaId: 'cardsArea', name: '卡牌典藏' },
    { tabId: 'tabMine', areaId: 'mineArea', name: '我的' },
    { tabId: 'tabRelief', areaId: 'clientArea', name: '解忧' },
  ];

  let allPass = true;
  tabTests.forEach(({ tabId, areaId, name }) => {
    const btn = doc.getElementById(tabId);
    const area = doc.getElementById(areaId);
    if (!btn || !area) {
      allPass = false;
      return;
    }

    btn.click();

    const isBtnActive = btn.classList.contains('active');
    const isAreaVisible = !area.classList.contains('hidden');

    if (isBtnActive && isAreaVisible) {
      console.log(`[PASS] 点击「${name}」(#${tabId}) -> 成功激活，显示 #${areaId}`);
    } else {
      console.log(`[FAIL] 点击「${name}」(#${tabId}) -> active=${isBtnActive}, visible=${isAreaVisible}`);
      allPass = false;
    }
  });

  console.log('Errors at end:', errors);
  if (allPass && errors.length === 0) {
    console.log('\n=== 全部 6 大顶栏标签页点击与视图切换测试 100% 通过 ===');
    process.exit(0);
  } else {
    console.log('\n=== 测试存在失败项 ===');
    process.exit(1);
  }
}, 50);
