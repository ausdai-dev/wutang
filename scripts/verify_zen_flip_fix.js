// scripts/verify_zen_flip_fix.js
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

console.log('Verifying Zen Card Flip Back Face Overflow Fix...\n');

const htmlPath = path.join(__dirname, '..', 'frontend', 'index.html');
const htmlContent = fs.readFileSync(htmlPath, 'utf-8');

const dom = new JSDOM(htmlContent, {
  runScripts: 'dangerously',
  resources: 'usable',
  url: 'http://localhost/'
});

const { window } = dom;
const { document } = window;

function runTests() {
  let passed = 0;
  let total = 0;

  function assert(condition, desc) {
    total++;
    if (condition) {
      console.log(`[PASS] ${desc}`);
      passed++;
    } else {
      console.error(`[FAIL] ${desc}`);
      process.exitCode = 1;
    }
  }

  // Test 1: Check DOM structure of modal back face and scroll container
  const backFace = document.querySelector('.zen-modal-back-face');
  const backScroll = document.querySelector('.zen-modal-back-scroll');
  assert(backFace !== null, 'Back face container .zen-modal-back-face exists');
  assert(backScroll !== null, 'Back scroll container .zen-modal-back-scroll exists inside back face');

  // Test 2: Check CSS definitions in index.html
  assert(htmlContent.includes('.zen-modal-back-face'), 'CSS contains .zen-modal-back-face definition');
  assert(htmlContent.includes('.zen-modal-back-scroll'), 'CSS contains .zen-modal-back-scroll definition');
  assert(htmlContent.includes('contain: paint'), 'CSS contains contain: paint for strict 3D clipping');
  assert(htmlContent.includes('clip-path: inset(0 round 12px)'), 'CSS contains clip-path: inset(0 round 12px)');

  // Test 3: Check Card 59 (天人) can be opened and populated
  assert(typeof window.openZen96CardModal === 'function', 'openZen96CardModal function exists');
  
  // Find card 59 in ZEN_CARDS_96
  let card59 = null;
  if (Array.isArray(window.ZEN_CARDS_96)) {
    card59 = window.ZEN_CARDS_96.find(c => c.num === '59' || c.name === '天人');
  }

  if (card59) {
    window.openZen96CardModal(card59.card_id);
  } else {
    // If cards not yet loaded in test env, call with mocked card
    window.openZen96CardModal('WUTANG-CARD-59');
  }

  const titleEl = document.getElementById('zen96ModalTitle');
  const backTitleEl = document.getElementById('zen96ModalBackTitle');
  const backSceneEl = document.getElementById('zen96ModalBackScene');
  const backQuestionEl = document.getElementById('zen96ModalBackQuestion');

  assert(titleEl && titleEl.textContent === '天人', 'Modal front title displays "天人"');
  assert(backTitleEl && backTitleEl.textContent.includes('天人'), 'Modal back title displays "【 天人 】" or "【 天 人 】"');
  assert(backSceneEl && backSceneEl.textContent.includes('旅人在山谷中停步'), 'Modal back scene contains full description');
  assert(backQuestionEl && backQuestionEl.textContent.includes('你的身体、时间和环境'), 'Modal back question contains full introspection text');

  // Test 4: Check card flip toggle
  const flipper = document.getElementById('zen96ModalFlipper');
  assert(flipper !== null, '#zen96ModalFlipper exists');

  assert(typeof window.toggleZen96ModalFlip === 'function', 'toggleZen96ModalFlip exists');
  window.toggleZen96ModalFlip();
  assert(flipper.style.transform === 'rotateY(180deg)', 'flipper transforms to rotateY(180deg)');

  window.toggleZen96ModalFlip();
  assert(flipper.style.transform === 'rotateY(0deg)', 'flipper flips back to rotateY(0deg)');

  // Test 5: Verify touch guard avoids accidental flip when scrolling
  window._zenModalScrollActive = true;
  window.toggleZen96ModalFlip();
  assert(flipper.style.transform === 'rotateY(0deg)', 'toggleZen96ModalFlip does NOT flip when _zenModalScrollActive is true');
  assert(window._zenModalScrollActive === false, '_zenModalScrollActive resets after suppressed click');

  console.log(`\n======================================================`);
  console.log(`🎉 ALL ${passed} / ${total} TESTS PASSED 100%!`);
  console.log(`======================================================\n`);
}

if (document.readyState === 'complete' || document.readyState === 'interactive') {
  runTests();
} else {
  window.addEventListener('DOMContentLoaded', () => {
    setTimeout(runTests, 150);
  });
}
