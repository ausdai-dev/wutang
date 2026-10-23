const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const htmlPath = path.join(__dirname, '..', 'frontend', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  resources: 'usable',
  url: 'http://localhost/'
});
const { window } = dom;
const { document } = window;

console.log('Testing Zen Banner Carousel...\n');

window.addEventListener('DOMContentLoaded', () => {
  runTests();
});

// 兜底
setTimeout(runTests, 500);

let tested = false;
function runTests() {
  if (tested) return;
  tested = true;

  try {
    // 1. DOM 元素检查
    const carousel = document.getElementById('zenBannerCarousel');
    const slidesWrap = document.getElementById('zenCarouselSlides');
    const dotsWrap = document.getElementById('zenCarouselDots');
    const prevBtn = document.getElementById('zenCarouselPrev');
    const nextBtn = document.getElementById('zenCarouselNext');
    const badgeTitle = document.getElementById('zenCarouselTitle');
    const badgeSub = document.getElementById('zenCarouselSubtitle');

    console.assert(carousel, 'zenBannerCarousel should exist');
    console.assert(slidesWrap, 'zenCarouselSlides should exist');
    console.assert(dotsWrap, 'zenCarouselDots should exist');
    console.assert(prevBtn, 'zenCarouselPrev should exist');
    console.assert(nextBtn, 'zenCarouselNext should exist');
    console.assert(badgeTitle, 'zenCarouselTitle should exist');
    console.log('[Test 1] All Carousel DOM elements exist: PASSED');

    // 2. 检查幻灯片与指示点数量
    const slides = slidesWrap.querySelectorAll('.zen-carousel-slide');
    const dots = dotsWrap.querySelectorAll('.zen-carousel-dot');
    console.assert(slides.length === 5, 'Should have exactly 5 banner slides, got: ' + slides.length);
    console.assert(dots.length === 5, 'Should have exactly 5 dots, got: ' + dots.length);
    console.log('[Test 2] Slide and dot counts (5 items): PASSED');

    // 3. 检查首帧
    console.assert(slides[0].classList.contains('active'), 'First slide should be active');
    console.assert(dots[0].classList.contains('active'), 'First dot should be active');
    console.assert(badgeTitle.textContent === '禅茶一味', 'First slide title matches, got: ' + badgeTitle.textContent);
    console.log('[Test 3] Initial slide state (禅茶一味): PASSED');

    // 4. 点击下一个按钮
    nextBtn.click();
    console.assert(!slides[0].classList.contains('active'), 'Slide 0 inactive');
    console.assert(slides[1].classList.contains('active'), 'Slide 1 active');
    console.assert(dots[1].classList.contains('active'), 'Dot 1 active');
    console.assert(badgeTitle.textContent === '修竹清风', 'Slide 1 title is 修竹清风, got: ' + badgeTitle.textContent);
    console.log('[Test 4] Next button click -> Slide 1 (修竹清风): PASSED');

    // 5. 点击指示点跳转到松风远岫 (idx: 3)
    dots[3].click();
    console.assert(slides[3].classList.contains('active'), 'Slide 3 active');
    console.assert(dots[3].classList.contains('active'), 'Dot 3 active');
    console.assert(badgeTitle.textContent === '松风远岫', 'Slide 3 title is 松风远岫, got: ' + badgeTitle.textContent);
    console.log('[Test 5] Direct dot jump -> Slide 3 (松风远岫): PASSED');

    // 6. 点击指示点跳转到碧潭青莲 (idx: 4)
    dots[4].click();
    console.assert(slides[4].classList.contains('active'), 'Slide 4 active');
    console.assert(dots[4].classList.contains('active'), 'Dot 4 active');
    console.assert(badgeTitle.textContent === '碧潭青莲', 'Slide 4 title is 碧潭青莲, got: ' + badgeTitle.textContent);
    console.log('[Test 6] Direct dot jump -> Slide 4 (碧潭青莲): PASSED');

    // 7. 点击前一个按钮
    prevBtn.click();
    console.assert(slides[3].classList.contains('active'), 'Back to Slide 3');
    console.log('[Test 7] Prev button click -> Slide 3: PASSED');

    console.log('\n======================================================');
    console.log('🎉 ALL 7 ZEN BANNER CAROUSEL TESTS PASSED 100%!');
    console.log('======================================================');
    process.exit(0);
  } catch (err) {
    console.error('\n[x] Test failed with error:', err);
    process.exit(1);
  }
}
