// scripts/test_awareness_vs_zen96.js
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', 'frontend', 'index.html'), 'utf-8');

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  resources: 'usable'
});

const { window } = dom;
const { document } = window;

function assert(condition, message) {
  if (!condition) {
    console.error('[FAIL]', message);
    process.exit(1);
  }
  console.log('[PASS]', message);
}

setTimeout(() => {
  // 1. Verify Awareness Card on home page
  const entryBtnCard = document.getElementById('entryBtnCard');
  assert(entryBtnCard !== null, '抽一张今日觉察牌按钮存在');
  entryBtnCard.click();

  const titleEl = document.getElementById('awFrontTitle');
  const qEl = document.getElementById('awFrontQuestion');
  assert(titleEl && titleEl.textContent.trim().length > 0, '今日觉察牌标题已渲染: ' + titleEl.textContent);
  assert(qEl && qEl.textContent.trim().length > 0, '今日觉察牌反思问句已渲染: ' + qEl.textContent);

  // Check that the title is one of the adult dilemmas (CARDS_MINDSET)
  const mindsetTitles = [
    '总想让所有人满意', '停不下来的思考', '不敢开始', '已经很累了',
    '为什么总是我的错', '害怕被拒绝', '担心明天失控', '同辈追赶焦虑',
    '不配得感', '悬在半空的心', '被评价绑架', '假装情绪稳定',
    '无法休息的内疚', '难以说出需要', '进退两难的摇摆', '不被理解的孤独'
  ];
  const isMindset = mindsetTitles.includes(titleEl.textContent.trim());
  assert(isMindset, '今日觉察牌标题属于 16 张内心情绪困扰牌之一: ' + titleEl.textContent);

  // 2. Verify Zen Wisdom shortcut button in home banner
  const btnDrawWisdom = document.getElementById('btnDrawZenWisdom');
  assert(btnDrawWisdom !== null, '首页「🍵 遇事不决？抽取今日东方锦囊/禅签」快捷按钮存在');

  // 3. Test clicking the Zen Wisdom Pouch
  btnDrawWisdom.click();
  const modal = document.getElementById('zen96Modal');
  assert(modal && !modal.classList.contains('hidden'), '点击抽取锦囊后，3D 东方禅意卡牌模态窗成功唤起');
  const modalTitle = document.getElementById('zen96ModalTitle');
  assert(modalTitle && modalTitle.textContent.length > 0, '锦囊模态窗标题已渲染: ' + modalTitle.textContent);
  const modalCore = document.getElementById('zen96ModalCore');
  assert(modalCore && modalCore.textContent.length > 0, '锦囊模态窗核心智慧已渲染: ' + modalCore.textContent);

  // 4. Test useZen96InRelief
  window.useZen96InRelief();
  assert(modal.classList.contains('hidden'), '将锦囊带入解忧处后模态窗关闭');
  const textarea = document.getElementById('userTextarea');
  assert(textarea && textarea.value.includes('东方锦囊'), '解忧输入框已自动填入锦囊智慧指引: ' + textarea.value.slice(0, 45) + '...');

  console.log('\n=== Option A 觉察牌与96张东方锦囊功能分离验证 100% 通过 ===\n');
  process.exit(0);
}, 300);
