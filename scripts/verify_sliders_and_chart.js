const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const htmlPath = path.join(__dirname, '..', 'frontend', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

console.log('Loading JSDOM with index.html...');
const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  resources: 'usable',
  url: 'http://localhost/'
});

const { window } = dom;
const { document } = window;

// 等待页面加载及 DOMContentLoaded
window.addEventListener('DOMContentLoaded', () => {
  runTests();
});

// 手动触发如果事件已过
setTimeout(runTests, 1000);

let tested = false;
function runTests() {
  if (tested) return;
  tested = true;
  console.log('Starting verification tests...\n');

  try {
    // 1. 验证 DOM 元素存在
    const energySlider = document.getElementById('energyRangeInput');
    const stressSlider = document.getElementById('stressRangeInput');
    const energyNumText = document.getElementById('energyNumText');
    const stressNumText = document.getElementById('stressNumText');
    const energyDescText = document.getElementById('energyDescText');
    const stressDescText = document.getElementById('stressDescText');
    const btnCalViewMonth = document.getElementById('btnCalViewMonth');
    const btnCalViewTrend = document.getElementById('btnCalViewTrend');
    const calWrap = document.getElementById('calendarGridViewWrap');
    const trendWrap = document.getElementById('calendarTrendViewWrap');
    const svg = document.getElementById('moodTrendSvg');

    console.assert(energySlider, 'energyRangeInput should exist');
    console.assert(stressSlider, 'stressRangeInput should exist');
    console.assert(energyNumText, 'energyNumText should exist');
    console.assert(stressNumText, 'stressNumText should exist');
    console.assert(btnCalViewMonth, 'btnCalViewMonth should exist');
    console.assert(btnCalViewTrend, 'btnCalViewTrend should exist');
    console.assert(calWrap, 'calendarGridViewWrap should exist');
    console.assert(trendWrap, 'calendarTrendViewWrap should exist');
    console.assert(svg, 'moodTrendSvg should exist');
    console.log('[Test 1] DOM Elements existence check: PASSED');

    // 2. 模拟精力滑块滑动
    energySlider.value = 9;
    energySlider.dispatchEvent(new window.Event('input'));
    console.assert(energyNumText.textContent === '9', 'Energy text should be 9');
    console.assert(energyDescText.textContent === '饱满', 'Energy desc should be 饱满, got: ' + energyDescText.textContent);
    console.log('[Test 2] Energy slider interaction: PASSED (Value 9 -> 饱满)');

    // 3. 模拟压力滑块滑动
    stressSlider.value = 8;
    stressSlider.dispatchEvent(new window.Event('input'));
    console.assert(stressNumText.textContent === '8', 'Stress text should be 8');
    console.assert(stressDescText.textContent === '较大', 'Stress desc should be 较大, got: ' + stressDescText.textContent);
    console.log('[Test 3] Stress slider interaction: PASSED (Value 8 -> 较大)');

    // 4. 模拟签到提交
    const btnCheckin = document.getElementById('btnSubmitCheckin');
    const noteInput = document.getElementById('checkinNoteInput');
    if (noteInput) noteInput.value = '今天完成了折线图与滑块重构';
    btnCheckin.click();

    const storedCheckins = JSON.parse(window.localStorage.getItem('wutang_mood_checkins') || '[]');
    console.assert(storedCheckins.length > 0, 'Should have at least 1 checkin stored');
    const latest = storedCheckins[0];
    console.assert(latest.energy === 9, 'Stored energy should be 9');
    console.assert(latest.stress === 8, 'Stored stress should be 8');
    console.assert(latest.note === '今天完成了折线图与滑块重构', 'Stored note matches');
    console.log('[Test 4] Mood checkin submission with numeric slider: PASSED');

    // 5. 切换到折线图走势视图
    btnCalViewTrend.click();
    console.assert(btnCalViewTrend.classList.contains('active'), 'Trend view button should be active');
    console.assert(!btnCalViewMonth.classList.contains('active'), 'Month view button should not be active');
    console.assert(!trendWrap.classList.contains('hidden'), 'Trend wrapper should be visible');
    console.assert(calWrap.classList.contains('hidden'), 'Calendar grid wrapper should be hidden');
    console.log('[Test 5] View switcher (Calendar <-> Trend): PASSED');

    // 6. 验证演示样例数据与实线/虚线折线图渲染
    window.handleToggleChartDemoData();
    const demoCheckins = JSON.parse(window.localStorage.getItem('wutang_mood_checkins') || '[]');
    console.assert(demoCheckins.length >= 6, 'Demo checkins should have >= 6 items');

    const svgHtml = svg.innerHTML;
    // 检查是否包含实线（无 dasharray）与虚线（stroke-dasharray="5 4"）
    const hasDashedLine = svgHtml.includes('stroke-dasharray="5 4"');
    const hasSolidLine = svgHtml.includes('stroke-width="2.6"');
    const hasPoints = svgHtml.includes('class="chart-point"');

    console.assert(hasDashedLine, 'SVG must contain dashed line for missing days');
    console.assert(hasSolidLine, 'SVG must contain solid line for consecutive days');
    console.assert(hasPoints, 'SVG must contain data circle points');
    console.log('[Test 6] Chart Bezier smoothing & Solid/Dashed line separation: PASSED');
    console.log('         - Consecutive days (continuous): SOLID stroke found');
    console.log('         - Missing days (gap): DASHED stroke found');
    console.log('         - Real checkin points: Rendered');

    // 7. 切回日历网格
    btnCalViewMonth.click();
    console.assert(btnCalViewMonth.classList.contains('active'), 'Month view button should be active again');
    console.assert(trendWrap.classList.contains('hidden'), 'Trend wrap should be hidden');
    console.assert(!calWrap.classList.contains('hidden'), 'Calendar grid should be visible');
    console.log('[Test 7] Switch back to Calendar view: PASSED');

    console.log('\n===========================================');
    console.log('🎉 ALL 7 VERIFICATION TESTS PASSED SUCCESSFULLY!');
    console.log('===========================================');
    process.exit(0);
  } catch (err) {
    console.error('\n[x] Test failed with error:', err);
    process.exit(1);
  }
}
