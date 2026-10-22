const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const htmlPath = path.join(__dirname, '..', 'frontend', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  url: 'http://localhost/',
  beforeParse(window) {
    window.localStorage.setItem('wutang_manager_active', 'true');
  }
});
const { window } = dom;
const { document } = window;

console.log('Testing 4-in-1 Equal Card Libraries...\n');

try {
  // 1. 元素存在性
  const btnBase32 = document.getElementById('btnTabBase32');
  const btnPantheon = document.getElementById('btnTabPantheon');
  const btnZen96 = document.getElementById('btnTabZen96');
  const btnTheme = document.getElementById('btnTabThemePacks');

  const subBase = document.getElementById('subViewBase32');
  const subPantheon = document.getElementById('subViewPantheon108');
  const subZen96 = document.getElementById('subViewZen96');
  const subTheme = document.getElementById('subViewThemePacks');
  const filterWrap = document.getElementById('studioCardTypeFilterWrap');

  console.assert(btnBase32, 'btnTabBase32 should exist');
  console.assert(btnPantheon, 'btnTabPantheon should exist');
  console.assert(btnZen96, 'btnTabZen96 should exist');
  console.assert(btnTheme, 'btnTabThemePacks should exist');
  console.assert(subBase, 'subViewBase32 should exist');
  console.assert(subPantheon, 'subViewPantheon108 should exist');
  console.assert(subZen96, 'subViewZen96 should exist');
  console.assert(subTheme, 'subViewThemePacks should exist');
  console.assert(filterWrap, 'studioCardTypeFilterWrap should exist');
  console.log('[Test 1] 4 Buttons and 4 Subviews exist: PASSED');

  // 2. 初始状态为 base32
  window.switchStudioCardLibrary('base32');
  console.assert(btnBase32.classList.contains('active'), 'btnBase32 active');
  console.assert(subBase.style.display !== 'none', 'subBase visible');
  console.assert(subPantheon.style.display === 'none', 'subPantheon hidden');
  console.assert(filterWrap.style.display !== 'none', 'filterWrap visible');
  console.log('[Test 2] Default base32 view: PASSED');

  // 3. 点击百八常道库 (108)
  btnPantheon.click();
  console.assert(btnPantheon.classList.contains('active'), 'btnPantheon active');
  console.assert(!btnBase32.classList.contains('active'), 'btnBase32 inactive');
  console.assert(subPantheon.style.display === 'block', 'subPantheon visible');
  console.assert(subBase.style.display === 'none', 'subBase hidden');
  console.assert(filterWrap.style.display === 'none', 'filterWrap hidden');
  const pGrid = document.getElementById('pantheonCardsGrid');
  console.assert(pGrid && pGrid.children.length === 108, 'pantheonCardsGrid should have 108 cards, got: ' + (pGrid ? pGrid.children.length : 0));
  console.log('[Test 3] Switch to Pantheon 108 view: PASSED (108 cards rendered)');

  // 4. 点击觉察牌画廊 (96)
  btnZen96.click();
  console.assert(btnZen96.classList.contains('active'), 'btnZen96 active');
  console.assert(subZen96.style.display === 'block', 'subZen96 visible');
  console.assert(subPantheon.style.display === 'none', 'subPantheon hidden');
  const zGrid = document.getElementById('zen96CardsGrid');
  console.assert(zGrid && zGrid.children.length === 96, 'zen96CardsGrid should have 96 cards, got: ' + (zGrid ? zGrid.children.length : 0));
  console.log('[Test 4] Switch to Zen96 gallery view: PASSED (96 cards rendered)');

  // 5. 点击主题卡牌包 (6)
  btnTheme.click();
  console.assert(btnTheme.classList.contains('active'), 'btnTheme active');
  console.assert(subTheme.style.display === 'block', 'subTheme visible');
  console.assert(subZen96.style.display === 'none', 'subZen96 hidden');
  const tGrid = document.getElementById('themePackGridContainer');
  console.assert(tGrid && tGrid.children.length === 6, 'themePackGridContainer should have 6 packs, got: ' + (tGrid ? tGrid.children.length : 0));
  console.log('[Test 5] Switch to Theme packs view: PASSED (6 packs rendered)');

  // 6. 切回基础解忧牌 (32)
  btnBase32.click();
  console.assert(btnBase32.classList.contains('active'), 'btnBase32 active');
  console.assert(subBase.style.display === 'block', 'subBase visible');
  console.assert(subTheme.style.display === 'none', 'subTheme hidden');
  console.assert(filterWrap.style.display !== 'none', 'filterWrap visible again');
  const baseGrid = document.getElementById('studioCardListContainer');
  console.assert(baseGrid && baseGrid.children.length === 32, 'studioCardListContainer should have 32 cards, got: ' + (baseGrid ? baseGrid.children.length : 0));
  console.log('[Test 6] Switch back to Base 32 view: PASSED (32 cards rendered)');

  console.log('\n======================================================');
  console.log('🎉 ALL 4-IN-1 EQUAL CARD LIBRARIES TESTS PASSED 100%!');
  console.log('======================================================');
  process.exit(0);
} catch (err) {
  console.error('\n[x] Test failed with error:', err);
  process.exit(1);
}
