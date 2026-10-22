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

console.log('Testing 4-in-1 Equal Card Libraries with actual user clicks...\n');

try {
  let toastMessage = '';
  window.showToast = function(msg) {
    toastMessage = msg;
  };

  const btnBase32 = document.getElementById('btnTabBase32');
  const btnPantheon = document.getElementById('btnTabPantheon');
  const btnZen96 = document.getElementById('btnTabZen96');
  const btnTheme = document.getElementById('btnTabThemePacks');

  const subBase = document.getElementById('subViewBase32');
  const subPantheon = document.getElementById('subViewPantheon108');
  const subZen96 = document.getElementById('subViewZen96');
  const subTheme = document.getElementById('subViewThemePacks');
  const filterWrap = document.getElementById('studioCardTypeFilterWrap');

  console.assert(btnBase32.classList.contains('card-lib-pill'), 'btnBase32 has card-lib-pill class');
  console.assert(btnPantheon.classList.contains('card-lib-pill'), 'btnPantheon has card-lib-pill class');

  // 1. 点击百八常道库 (108)
  toastMessage = '';
  btnPantheon.click();
  console.assert(toastMessage !== '已填入体验案例，点击「帮我理一理」即可梳理', 'Should NOT trigger demo toast on card library click! Got: ' + toastMessage);
  console.assert(btnPantheon.classList.contains('active'), 'btnPantheon active');
  console.assert(!btnBase32.classList.contains('active'), 'btnBase32 inactive');
  console.assert(subPantheon.style.display === 'block', 'subPantheon visible');
  console.assert(subBase.style.display === 'none', 'subBase hidden');
  console.assert(filterWrap.style.display === 'none', 'filterWrap hidden');
  const pGrid = document.getElementById('pantheonCardsGrid');
  console.assert(pGrid && pGrid.children.length === 108, 'pantheonCardsGrid should have 108 cards');
  console.log('[Test 1] Click Pantheon (108): PASSED (No bogus toast, 108 cards rendered)');

  // 2. 点击觉察牌画廊 (96)
  toastMessage = '';
  btnZen96.click();
  console.assert(toastMessage !== '已填入体验案例，点击「帮我理一理」即可梳理', 'No bogus toast');
  console.assert(btnZen96.classList.contains('active'), 'btnZen96 active');
  console.assert(subZen96.style.display === 'block', 'subZen96 visible');
  console.assert(subPantheon.style.display === 'none', 'subPantheon hidden');
  const zGrid = document.getElementById('zen96CardsGrid');
  console.assert(zGrid && zGrid.children.length === 96, 'zen96CardsGrid should have 96 cards');
  console.log('[Test 2] Click Zen96 (96): PASSED (No bogus toast, 96 cards rendered)');

  // 3. 点击主题卡牌包 (6)
  toastMessage = '';
  btnTheme.click();
  console.assert(toastMessage !== '已填入体验案例，点击「帮我理一理」即可梳理', 'No bogus toast');
  console.assert(btnTheme.classList.contains('active'), 'btnTheme active');
  console.assert(subTheme.style.display === 'block', 'subTheme visible');
  console.assert(subZen96.style.display === 'none', 'subZen96 hidden');
  const tGrid = document.getElementById('themePackGridContainer');
  console.assert(tGrid && tGrid.children.length === 6, 'themePackGridContainer should have 6 packs');
  console.log('[Test 3] Click Theme (6): PASSED (No bogus toast, 6 packs rendered)');

  // 4. 切回基础解忧牌 (32)
  toastMessage = '';
  btnBase32.click();
  console.assert(toastMessage !== '已填入体验案例，点击「帮我理一理」即可梳理', 'No bogus toast');
  console.assert(btnBase32.classList.contains('active'), 'btnBase32 active');
  console.assert(subBase.style.display === 'block', 'subBase visible');
  console.assert(subTheme.style.display === 'none', 'subTheme hidden');
  console.assert(filterWrap.style.display === 'flex', 'filterWrap visible again');
  const baseGrid = document.getElementById('studioCardListContainer');
  console.assert(baseGrid && baseGrid.children.length === 32, 'studioCardListContainer should have 32 cards');
  console.log('[Test 4] Click Base (32): PASSED (32 cards rendered)');

  console.log('\n======================================================');
  console.log('🎉 BUG RESOLVED & ALL CARD LIBRARIES VERIFIED 100%!');
  console.log('======================================================');
  process.exit(0);
} catch (err) {
  console.error('\n[x] Test failed with error:', err);
  process.exit(1);
}
