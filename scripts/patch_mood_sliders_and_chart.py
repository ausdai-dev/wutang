# -*- coding: utf-8 -*-
"""
补丁脚本：将精力状态与主观压力感受改为数字滑块，并为心境日历增加插值平滑折线图视图（有日结实线，没日记虚线）
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

def main():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. CSS 补充
    m_css = re.search(r'(\.level-pill\.active\s*\{[^}]+\})', content)
    if not m_css:
        raise RuntimeError("CSS anchor not found in _template.html")

    new_css = m_css.group(1) + """

/* 现代东方数字滑块定制样式 */
.slider-control-card {
  background: var(--color-surface-subtle);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px 14px;
  box-sizing: border-box;
  transition: border-color var(--trans), box-shadow var(--trans);
}
.slider-control-card:hover {
  border-color: var(--color-border-dark);
  box-shadow: 0 2px 8px rgba(34,31,27,0.03);
}
.slider-wrapper {
  position: relative;
  padding: 4px 2px 2px;
}
.wt-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 6px;
  outline: none;
  background: #E8E2D6;
  transition: background 0.15s ease;
  cursor: pointer;
  margin: 10px 0 6px;
}
.wt-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #FFFFFF;
  border: 2.5px solid var(--slider-thumb-color, var(--color-primary));
  box-shadow: 0 2px 6px rgba(34,31,27,0.18);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.wt-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 10px rgba(34,31,27,0.25);
}
.wt-slider::-webkit-slider-thumb:active {
  transform: scale(1.05);
}
.wt-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #FFFFFF;
  border: 2.5px solid var(--slider-thumb-color, var(--color-primary));
  box-shadow: 0 2px 6px rgba(34,31,27,0.18);
  cursor: pointer;
  transition: transform 0.15s ease;
}
.wt-slider-energy {
  --slider-thumb-color: #3A6D4F;
}
.wt-slider-stress {
  --slider-thumb-color: #8E2927;
}

/* 日历与心境走势视图切换与图表样式 */
.view-toggle-btn {
  border: none;
  background: transparent;
  color: var(--color-muted);
  padding: 5px 12px;
  border-radius: 16px;
  font-size: 12.5px;
  cursor: pointer;
  transition: all var(--trans);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.view-toggle-btn.active {
  background: var(--color-surface) !important;
  color: var(--color-ink) !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 4px rgba(34,31,27,0.08) !important;
}
.view-toggle-btn:not(.active):hover {
  color: var(--color-ink) !important;
}
.mood-trend-chart-card {
  background: #FFFFFF;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px 14px 12px;
  position: relative;
  box-sizing: border-box;
}
.chart-tooltip {
  position: absolute;
  pointer-events: none;
  background: rgba(34, 31, 27, 0.94);
  color: #FFFFFF;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 12px;
  line-height: 1.5;
  box-shadow: 0 6px 18px rgba(0,0,0,0.22);
  backdrop-filter: blur(4px);
  transition: opacity 0.12s ease;
  z-index: 25;
  white-space: nowrap;
}
.chart-point {
  cursor: pointer;
  transition: r 0.15s ease;
}
.chart-point:hover {
  r: 6.5px;
}
"""
    content = content[:m_css.start()] + new_css + content[m_css.end():]

    # 2. HTML 替换：将精力状态与主观压力单选药丸组改为数字滑块
    p_sliders = re.search(r'<div style="display:grid;grid-template-columns:repeat\(auto-fit,\s*minmax\(220px,\s*1fr\)\);gap:14px;margin-top:14px;">.*?id="stressPillGroup".*?</div>\s*</div>\s*</div>', content, re.DOTALL)
    if not p_sliders:
        raise RuntimeError("p_sliders anchor not found in _template.html")

    new_sliders_html = """<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:16px;margin-top:16px;margin-bottom:12px;">

          <!-- 精力状态数字滑块 (1-10分) -->
          <div class="slider-control-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <div class="section-label" style="font-size:13px;margin:0;font-weight:600;color:var(--color-ink);">当前的精力状态：</div>
              <div class="slider-value-badge" id="energyValueBadge" style="background:var(--color-success-bg);color:var(--color-success);border:1px solid var(--color-success-border);padding:3px 10px;border-radius:14px;font-size:12.5px;font-weight:600;display:inline-flex;align-items:center;gap:4px;">
                <span id="energyNumText" style="font-size:14px;font-family:var(--font-serif);font-weight:bold;">6</span>
                <span style="opacity:0.6;font-size:11px;">/ 10</span>
                <span style="opacity:0.4;">·</span>
                <span id="energyDescText">平稳</span>
              </div>
            </div>
            <div class="slider-wrapper">
              <input type="range" id="energyRangeInput" min="1" max="10" step="1" value="6" class="wt-slider wt-slider-energy" aria-label="当前的精力状态滑块">
              <div class="slider-scale-labels" style="display:flex;justify-content:space-between;font-size:11px;color:var(--color-muted);margin-top:4px;padding:0 2px;">
                <span>1 透支</span>
                <span>3 疲惫</span>
                <span>5 平稳</span>
                <span>7 充沛</span>
                <span>10 饱满</span>
              </div>
            </div>
          </div>

          <!-- 主观压力感受数字滑块 (1-10分) -->
          <div class="slider-control-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
              <div class="section-label" style="font-size:13px;margin:0;font-weight:600;color:var(--color-ink);">主观压力感受：</div>
              <div class="slider-value-badge" id="stressValueBadge" style="background:var(--color-gold-bg);color:var(--color-gold);border:1px solid var(--color-gold-border);padding:3px 10px;border-radius:14px;font-size:12.5px;font-weight:600;display:inline-flex;align-items:center;gap:4px;">
                <span id="stressNumText" style="font-size:14px;font-family:var(--font-serif);font-weight:bold;">3</span>
                <span style="opacity:0.6;font-size:11px;">/ 10</span>
                <span style="opacity:0.4;">·</span>
                <span id="stressDescText">较轻</span>
              </div>
            </div>
            <div class="slider-wrapper">
              <input type="range" id="stressRangeInput" min="1" max="10" step="1" value="3" class="wt-slider wt-slider-stress" aria-label="主观压力感受滑块">
              <div class="slider-scale-labels" style="display:flex;justify-content:space-between;font-size:11px;color:var(--color-muted);margin-top:4px;padding:0 2px;">
                <span>1 极轻</span>
                <span>3 较轻</span>
                <span>5 中等</span>
                <span>7 较大</span>
                <span>10 极大</span>
              </div>
            </div>
          </div>

        </div>"""
    content = content[:p_sliders.start()] + new_sliders_html + content[p_sliders.end():]

    # 3. HTML 替换：心境日历模块支持两个视图切换与折线图容器
    p_cal = re.search(r'<!-- 模块 4: 心境日历.*?<div class="mini-calendar-grid" id="miniCalendarGrid"></div>', content, re.DOTALL)
    if not p_cal:
        raise RuntimeError("p_cal anchor not found in _template.html")

    new_cal_header_html = """<!-- 模块 4: 心境日历与成长线索 (F-13 / 18.4) -->

      <section class="card" id="moodCalendarCardSection">

        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px;">

          <div>

            <h2 style="font-family:var(--font-serif);margin:0 0 4px;font-size:22px;">心境日历与成长线索</h2>

          </div>

          <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">

            <!-- 视图切换按钮：日历网格 vs 心境走势折线图 -->
            <div class="calendar-view-toggle" id="calViewToggle" style="display:inline-flex;background:var(--color-surface-subtle);border:1px solid var(--color-border);border-radius:20px;padding:3px;gap:2px;">

              <button type="button" class="view-toggle-btn active" id="btnCalViewMonth" style="border:none;background:var(--color-surface);color:var(--color-ink);padding:4px 12px;border-radius:16px;font-size:12.5px;cursor:pointer;font-weight:600;box-shadow:var(--shadow-sm);transition:all var(--trans);display:inline-flex;align-items:center;gap:4px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                日历网格
              </button>

              <button type="button" class="view-toggle-btn" id="btnCalViewTrend" style="border:none;background:transparent;color:var(--color-muted);padding:4px 12px;border-radius:16px;font-size:12.5px;cursor:pointer;transition:all var(--trans);display:inline-flex;align-items:center;gap:4px;">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                心境走势
              </button>

            </div>

            <div style="font-size:12.5px;color:var(--color-muted);background:var(--color-surface-subtle);border:1px solid var(--color-border);padding:3px 10px;border-radius:14px;" id="calMonthLabel">2026 年 10 月</div>

          </div>

        </div>



        <!-- 视图 1: 经典日历网格视图 -->

        <div id="calendarGridViewWrap">

          <div class="mini-calendar-grid" id="miniCalendarGrid"></div>

        </div>



        <!-- 视图 2: 插值平滑折线图视图 -->

        <div id="calendarTrendViewWrap" class="hidden">

          <div class="mood-trend-chart-card">

            <!-- 顶部图例与说明 -->
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:10px;padding-bottom:8px;border-bottom:1px dashed var(--color-border);">
              <div style="font-size:12px;color:var(--color-muted);display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
                <span style="display:inline-flex;align-items:center;gap:6px;">
                  <span style="display:inline-block;width:18px;height:3px;background:#3A6D4F;border-radius:2px;"></span>
                  <span style="color:#3A6D4F;font-weight:600;">精力走势 (1-10)</span>
                </span>
                <span style="display:inline-flex;align-items:center;gap:6px;">
                  <span style="display:inline-block;width:18px;height:3px;background:#8E2927;border-radius:2px;"></span>
                  <span style="color:#8E2927;font-weight:600;">主观压力 (1-10)</span>
                </span>
                <span style="color:var(--color-muted);font-size:11.5px;background:var(--color-surface-subtle);padding:2px 8px;border-radius:10px;border:1px solid var(--color-border);">
                  实线：连续日结 · 虚线：缺卡平滑插值
                </span>
              </div>
              <div style="display:flex;align-items:center;gap:8px;">
                <span id="chartDataStatsText" style="font-size:11.5px;color:var(--color-muted);">当月已修：0 天</span>
                <button type="button" id="btnChartDemoToggle" class="btn ghost sm" style="font-size:11px;padding:2px 8px;height:24px;line-height:20px;" onclick="handleToggleChartDemoData()">体验样例</button>
              </div>
            </div>

            <!-- SVG 响应式画布容器 -->
            <div style="position:relative;width:100%;min-height:230px;overflow:hidden;" id="trendChartSvgWrapper">
              <!-- SVG 动态插入 -->
              <svg id="moodTrendSvg" style="width:100%;height:230px;display:block;" viewBox="0 0 800 230" preserveAspectRatio="none"></svg>

              <!-- 悬停信息浮窗 Tooltip -->
              <div id="trendChartTooltip" class="chart-tooltip" style="display:none;opacity:0;"></div>
            </div>

          </div>

        </div>"""
    content = content[:p_cal.start()] + new_cal_header_html + content[p_cal.end():]

    # 4. JS 逻辑替换：initGrowthModule 中的精力与压力事件绑定与签到保存
    p_js = re.search(r'var currentSelectedMoods = \[\'calm\'\];.*?updateDataSummary\(\);\s*};', content, re.DOTALL)
    if not p_js:
        raise RuntimeError("p_js anchor not found in _template.html")

    new_js_growth = """var currentSelectedMoods = ['calm'];

  var currentEnergyValue = 6;

  var currentStressValue = 3;

  var currentSelectedEnergy = 6;

  var currentSelectedStress = 3;

  var currentCalendarView = 'calendar'; // 'calendar' | 'trend'

  function getEnergyMeta(val) {
    val = Number(val);
    if (val <= 2) return { text: '透支', level: 'drained', color: '#8E2927', bg: '#FDF3F3', border: '#F2D0D0' };
    if (val <= 4) return { text: '疲惫', level: 'low', color: '#996827', bg: '#FCF5E8', border: '#EFE0C4' };
    if (val <= 6) return { text: '平稳', level: 'normal', color: '#3A6D4F', bg: '#EDF6F1', border: '#C8DFD1' };
    if (val <= 8) return { text: '充沛', level: 'high', color: '#2E7D32', bg: '#E8F5E9', border: '#C8E6C9' };
    return { text: '饱满', level: 'high', color: '#1B5E20', bg: '#E8F5E9', border: '#A5D6A7' };
  }

  function getStressMeta(val) {
    val = Number(val);
    if (val <= 2) return { text: '极轻', level: 'very_low', color: '#3A6D4F', bg: '#EDF6F1', border: '#C8DFD1' };
    if (val <= 4) return { text: '较轻', level: 'low', color: '#9F7430', bg: '#FCF6EC', border: '#E9DABF' };
    if (val <= 6) return { text: '中等', level: 'moderate', color: '#996827', bg: '#FCF5E8', border: '#EFE0C4' };
    if (val <= 8) return { text: '较大', level: 'high', color: '#B74134', bg: '#FDF3F3', border: '#F2D0D0' };
    return { text: '极大', level: 'very_high', color: '#8E2927', bg: '#FBE9E7', border: '#FFCCBC' };
  }

  function updateSliderFill(slider, activeColor) {
    if (!slider) return;
    var min = Number(slider.min) || 1;
    var max = Number(slider.max) || 10;
    var val = Number(slider.value);
    var pct = ((val - min) / (max - min)) * 100;
    slider.style.background = 'linear-gradient(to right, ' + activeColor + ' 0%, ' + activeColor + ' ' + pct + '%, #E8E2D6 ' + pct + '%, #E8E2D6 100%)';
  }

  function initGrowthModule() {

    // 情绪标签选择

    var chipGroup = $('moodChipGroup');

    if (chipGroup) {

      chipGroup.addEventListener('click', function(e) {

        var chip = e.target.closest('.mood-chip');

        if (!chip) return;

        var mood = chip.getAttribute('data-mood');

        chip.classList.toggle('active');

        if (chip.classList.contains('active')) {

          if (currentSelectedMoods.indexOf(mood) === -1) currentSelectedMoods.push(mood);

        } else {

          currentSelectedMoods = currentSelectedMoods.filter(function(m) { return m !== mood; });

        }

      });

    }

    // 精力状态数字滑块
    var energySlider = $('energyRangeInput');
    if (energySlider) {
      var updateEnergyDisplay = function() {
        currentEnergyValue = parseInt(energySlider.value, 10) || 6;
        currentSelectedEnergy = currentEnergyValue;
        var meta = getEnergyMeta(currentEnergyValue);
        if ($('energyNumText')) $('energyNumText').textContent = currentEnergyValue;
        if ($('energyDescText')) $('energyDescText').textContent = meta.text;
        var badge = $('energyValueBadge');
        if (badge) {
          badge.style.color = meta.color;
          badge.style.backgroundColor = meta.bg;
          badge.style.borderColor = meta.border;
        }
        updateSliderFill(energySlider, meta.color);
      };
      energySlider.addEventListener('input', updateEnergyDisplay);
      updateEnergyDisplay();
    }

    // 主观压力数字滑块
    var stressSlider = $('stressRangeInput');
    if (stressSlider) {
      var updateStressDisplay = function() {
        currentStressValue = parseInt(stressSlider.value, 10) || 3;
        currentSelectedStress = currentStressValue;
        var meta = getStressMeta(currentStressValue);
        if ($('stressNumText')) $('stressNumText').textContent = currentStressValue;
        if ($('stressDescText')) $('stressDescText').textContent = meta.text;
        var badge = $('stressValueBadge');
        if (badge) {
          badge.style.color = meta.color;
          badge.style.backgroundColor = meta.bg;
          badge.style.borderColor = meta.border;
        }
        updateSliderFill(stressSlider, meta.color);
      };
      stressSlider.addEventListener('input', updateStressDisplay);
      updateStressDisplay();
    }

    // 初始化日历/走势图视图切换按钮
    initCalendarViewToggle();

    // 提交签到
    var btnCheckin = $('btnSubmitCheckin');

    if (btnCheckin) {

      btnCheckin.onclick = function() {

        var note = $('checkinNoteInput') ? $('checkinNoteInput').value.trim() : '';

        var todayStr = new Date().toISOString().slice(0, 10);

        var eMeta = getEnergyMeta(currentEnergyValue);
        var sMeta = getStressMeta(currentStressValue);

        var record = {

          checkin_id: 'MC-' + todayStr + '-' + Math.random().toString(36).slice(2, 6),

          date: todayStr,

          moods: currentSelectedMoods.slice(),

          energy: currentEnergyValue,

          energy_level: eMeta.level,

          stress: currentStressValue,

          stress_level: sMeta.level,

          note: note,

          created_at: new Date().toISOString()

        };

        var list = getStorageJson('wutang_mood_checkins', []);

        // 若今天已有记录，替换为最新记录或排在最前
        list = list.filter(function(item) { return item.date !== todayStr; });
        list.unshift(record);

        setStorageJson('wutang_mood_checkins', list);

        showToast('已留下今日心境印记');

        var box = $('checkinFeedbackBox');

        if (box) box.classList.remove('hidden');

        renderMiniCalendar();

        renderMoodTrendChart();

        updateDataSummary();

      };"""
    content = content[:p_js.start()] + new_js_growth + content[p_js.end():]

    # 5. JS 替换：添加视图切换函数与平滑折线图 renderMoodTrendChart
    p_js2 = re.search(r'function renderGrowthSection\(\)\s*\{.*?function renderMiniCalendar\(\)', content, re.DOTALL)
    if not p_js2:
        raise RuntimeError("p_js2 anchor not found in _template.html")

    new_js_render_growth = """function renderGrowthSection() {

    renderMiniCalendar();

    renderMoodTrendChart();

    // 渲染今日日期

    var badge = $('checkinTodayDateBadge');

    if (badge) badge.textContent = '今日：' + new Date().toISOString().slice(0, 10);

  }

  function initCalendarViewToggle() {
    var btnCal = $('btnCalViewMonth');
    var btnTrend = $('btnCalViewTrend');
    var calWrap = $('calendarGridViewWrap');
    var trendWrap = $('calendarTrendViewWrap');

    if (btnCal && btnTrend) {
      btnCal.onclick = function() {
        currentCalendarView = 'calendar';
        btnCal.classList.add('active');
        btnTrend.classList.remove('active');
        if (calWrap) calWrap.classList.remove('hidden');
        if (trendWrap) trendWrap.classList.add('hidden');
        renderMiniCalendar();
      };

      btnTrend.onclick = function() {
        currentCalendarView = 'trend';
        btnTrend.classList.add('active');
        btnCal.classList.remove('active');
        if (calWrap) calWrap.classList.add('hidden');
        if (trendWrap) trendWrap.classList.remove('hidden');
        renderMoodTrendChart();
      };
    }
  }

  // 辅助解析数值（兼容旧版字符串数据）
  function parseEnergyNumber(val) {
    if (typeof val === 'number') return Math.max(1, Math.min(10, val));
    var map = { high: 8, normal: 6, low: 4, drained: 2 };
    return map[val] || 6;
  }

  function parseStressNumber(val) {
    if (typeof val === 'number') return Math.max(1, Math.min(10, val));
    var map = { very_low: 2, low: 4, moderate: 6, high: 8, very_high: 10 };
    return map[val] || 3;
  }

  // 平滑三次贝塞尔连接曲线构建
  function buildBezierCurveCommand(p0, p1, t) {
    var tension = (typeof t === 'number') ? t : 0.35;
    var dx = p1.x - p0.x;
    var cp1x = p0.x + dx * tension;
    var cp1y = p0.y;
    var cp2x = p1.x - dx * tension;
    var cp2y = p1.y;
    return 'C ' + cp1x.toFixed(1) + ',' + cp1y.toFixed(1) + ' ' + cp2x.toFixed(1) + ',' + cp2y.toFixed(1) + ' ' + p1.x.toFixed(1) + ',' + p1.y.toFixed(1);
  }

  // 演示样例数据注入/清除（方便用户体验实线与虚线折线走势）
  window.handleToggleChartDemoData = function() {
    var checkins = getStorageJson('wutang_mood_checkins', []);
    var now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth();
    var mStr = year + '-' + String(month + 1).padStart(2, '0');

    var hasDemo = checkins.some(function(c) { return c && c.is_demo_sample; });
    if (hasDemo) {
      checkins = checkins.filter(function(c) { return !c.is_demo_sample; });
      setStorageJson('wutang_mood_checkins', checkins);
      showToast('已清空演示样例数据');
      if ($('btnChartDemoToggle')) $('btnChartDemoToggle').textContent = '体验样例';
    } else {
      // 构造一组有连续日结（实线）和缺席断档（虚线）的真实测试样本
      var samples = [
        { d: '02', energy: 7, stress: 3, note: '早起静坐 15 分钟，神清气爽' },
        { d: '03', energy: 8, stress: 2, note: '连续两天早睡，精力充沛' },
        // 缺席 4, 5, 6 号
        { d: '07', energy: 5, stress: 5, note: '节后返岗，有些杂事缠身' },
        { d: '08', energy: 4, stress: 6, note: '连续开了三个长会，略显疲惫' },
        // 缺席 9, 10 号
        { d: '11', energy: 6, stress: 4, note: '下午散步半小时，慢慢找回节律' },
        { d: '12', energy: 8, stress: 2, note: '心绪安宁，按时打卡' }
      ];
      samples.forEach(function(s) {
        var dt = mStr + '-' + s.d;
        checkins = checkins.filter(function(c) { return c.date !== dt; });
        var eMeta = getEnergyMeta(s.energy);
        var sMeta = getStressMeta(s.stress);
        checkins.push({
          checkin_id: 'DEMO-' + dt,
          date: dt,
          moods: ['calm'],
          energy: s.energy,
          energy_level: eMeta.level,
          stress: s.stress,
          stress_level: sMeta.level,
          note: s.note,
          is_demo_sample: true,
          created_at: new Date().toISOString()
        });
      });
      setStorageJson('wutang_mood_checkins', checkins);
      showToast('已载入 6 天心境演示数据（含实线与虚线段）');
      if ($('btnChartDemoToggle')) $('btnChartDemoToggle').textContent = '清除样例';
    }

    renderMiniCalendar();
    renderMoodTrendChart();
    updateDataSummary();
  };

  // 核心渲染：基于插值的平滑折线图（有日结实线连接，没日记虚线连接）
  function renderMoodTrendChart() {
    var svg = $('moodTrendSvg');
    if (!svg) return;

    var checkins = getStorageJson('wutang_mood_checkins', []);
    var journals = getStorageJson('wutang_journals', []);

    var now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth();
    var daysInMonth = new Date(year, month + 1, 0).getDate();
    var monthStr = year + '-' + String(month + 1).padStart(2, '0');

    // 筛选当月日记，建立索引
    var journalDateSet = {};
    journals.forEach(function(j) {
      if (j && j.date) journalDateSet[j.date] = j;
    });

    // 筛选当月签到记录（同一天以最新一条为准）
    var dayRecords = {};
    checkins.forEach(function(c) {
      if (c && c.date && c.date.indexOf(monthStr) === 0) {
        var dayNum = parseInt(c.date.slice(8, 10), 10);
        if (!dayRecords[dayNum]) {
          dayRecords[dayNum] = {
            day: dayNum,
            date: c.date,
            energy: parseEnergyNumber(c.energy),
            stress: parseStressNumber(c.stress),
            note: c.note || '',
            moods: c.moods || [],
            hasJournal: Boolean(journalDateSet[c.date]),
            isReal: true
          };
        }
      }
    });

    var validDays = Object.keys(dayRecords).map(function(k) { return parseInt(k, 10); }).sort(function(a, b) { return a - b; });

    var statsText = $('chartDataStatsText');
    if (statsText) {
      statsText.textContent = '当月已修：' + validDays.length + ' 天 / ' + daysInMonth + ' 天';
    }

    // 画布尺寸定义
    var W = 800;
    var H = 230;
    var padL = 52;
    var padR = 26;
    var padT = 24;
    var padB = 36;
    var plotW = W - padL - padR;
    var plotH = H - padT - padB;

    function getX(d) {
      if (daysInMonth <= 1) return padL + plotW / 2;
      return padL + ((d - 1) / (daysInMonth - 1)) * plotW;
    }

    function getY(val) {
      val = Math.max(0, Math.min(10, val));
      return padT + plotH - (val / 10) * plotH;
    }

    var svgContent = '';

    // 1. 背景与水平刻度线（0, 2, 4, 6, 8, 10）
    var yTicks = [
      { val: 10, label: '10 极高' },
      { val: 8, label: '8 充沛' },
      { val: 6, label: '6 平稳' },
      { val: 4, label: '4 疲累' },
      { val: 2, label: '2 预警' },
      { val: 0, label: '0' }
    ];

    yTicks.forEach(function(t) {
      var y = getY(t.val);
      var isCenter = (t.val === 6 || t.val === 5);
      var strokeColor = isCenter ? 'rgba(159, 116, 48, 0.25)' : 'rgba(34, 31, 27, 0.08)';
      var dash = isCenter ? '3 3' : '2 2';
      svgContent += '<line x1="' + padL + '" y1="' + y.toFixed(1) + '" x2="' + (padL + plotW) + '" y2="' + y.toFixed(1) + '" stroke="' + strokeColor + '" stroke-dasharray="' + dash + '" stroke-width="1" />';
      svgContent += '<text x="' + (padL - 10) + '" y="' + (y + 4).toFixed(1) + '" fill="var(--color-muted)" font-size="10.5" text-anchor="end" font-family="var(--font-sans)">' + t.label + '</text>';
    });

    // 2. X 轴底线与关键日期标注
    var baseY = getY(0);
    svgContent += '<line x1="' + padL + '" y1="' + baseY.toFixed(1) + '" x2="' + (padL + plotW) + '" y2="' + baseY.toFixed(1) + '" stroke="var(--color-border)" stroke-width="1.2" />';

    for (var d = 1; d <= daysInMonth; d++) {
      if (d === 1 || d === 5 || d === 10 || d === 15 || d === 20 || d === 25 || d === daysInMonth) {
        var x = getX(d);
        svgContent += '<line x1="' + x.toFixed(1) + '" y1="' + baseY.toFixed(1) + '" x2="' + x.toFixed(1) + '" y2="' + (baseY + 4).toFixed(1) + '" stroke="var(--color-border-dark)" stroke-width="1" />';
        svgContent += '<text x="' + x.toFixed(1) + '" y="' + (baseY + 16).toFixed(1) + '" fill="var(--color-muted)" font-size="10.5" text-anchor="middle" font-family="var(--font-sans)">' + d + '日</text>';
      }
    }

    // 3. 空状态展示（当没有任何打卡数据时）
    if (validDays.length === 0) {
      svgContent += '<rect x="' + (W / 2 - 170) + '" y="' + (H / 2 - 32) + '" width="340" height="58" rx="10" fill="rgba(253, 251, 248, 0.95)" stroke="var(--color-border)" stroke-width="1" filter="drop-shadow(0 2px 6px rgba(0,0,0,0.04))" />';
      svgContent += '<text x="' + (W / 2) + '" y="' + (H / 2 - 6) + '" fill="var(--color-ink)" font-size="13" font-weight="600" text-anchor="middle" font-family="var(--font-serif)">本月暂无心境日结记录</text>';
      svgContent += '<text x="' + (W / 2) + '" y="' + (H / 2 + 15) + '" fill="var(--color-muted)" font-size="11.5" text-anchor="middle">在上方留下今日心境印记，将自动在此生成起伏走势</text>';
      svg.innerHTML = svgContent;
      return;
    }

    // 4. 数据点坐标准备
    var energyPoints = [];
    var stressPoints = [];
    validDays.forEach(function(d) {
      var rec = dayRecords[d];
      energyPoints.push({ d: d, x: getX(d), y: getY(rec.energy), val: rec.energy, rec: rec });
      stressPoints.push({ d: d, x: getX(d), y: getY(rec.stress), val: rec.stress, rec: rec });
    });

    // 5. 核心：绘制插值平滑折线（实线连接 vs 虚线连接）
    // 规则：
    // - 若相邻两点日期差为 1 (连续日结)：实线连接
    // - 若相邻两点日期差 > 1 (中间缺失打卡/日记)：虚线连接
    function renderCurveSegments(points, strokeColor, seriesName) {
      var pathsHtml = '';
      if (points.length < 2) return pathsHtml;

      for (var i = 0; i < points.length - 1; i++) {
        var pA = points[i];
        var pB = points[i + 1];
        var isContinuous = (pB.d - pA.d === 1);
        var cmd = 'M ' + pA.x.toFixed(1) + ',' + pA.y.toFixed(1) + ' ' + buildBezierCurveCommand(pA, pB, 0.38);

        if (isContinuous) {
          // 有日结的实线连接
          pathsHtml += '<path d="' + cmd + '" fill="none" stroke="' + strokeColor + '" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.95" />';
        } else {
          // 没日记/缺卡的虚线连接（平滑插值过渡）
          pathsHtml += '<path d="' + cmd + '" fill="none" stroke="' + strokeColor + '" stroke-width="2.2" stroke-dasharray="5 4" stroke-linecap="round" stroke-linejoin="round" opacity="0.75" />';
        }
      }
      return pathsHtml;
    }

    // 渲染精力线与压力线
    svgContent += renderCurveSegments(energyPoints, '#3A6D4F', '精力');
    svgContent += renderCurveSegments(stressPoints, '#8E2927', '压力');

    // 6. 绘制实体打卡圆点
    energyPoints.forEach(function(p) {
      var r = 4.2;
      svgContent += '<circle cx="' + p.x.toFixed(1) + '" cy="' + p.y.toFixed(1) + '" r="' + r + '" fill="#FFFFFF" stroke="#3A6D4F" stroke-width="2.4" class="chart-point" data-type="energy" data-day="' + p.d + '" />';
      // 若当天同时有 AI 日记，绘制金色光环
      if (p.rec.hasJournal) {
        svgContent += '<circle cx="' + p.x.toFixed(1) + '" cy="' + p.y.toFixed(1) + '" r="7.5" fill="none" stroke="#9F7430" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.85" />';
      }
    });

    stressPoints.forEach(function(p) {
      var r = 4.2;
      svgContent += '<circle cx="' + p.x.toFixed(1) + '" cy="' + p.y.toFixed(1) + '" r="' + r + '" fill="#FFFFFF" stroke="#8E2927" stroke-width="2.4" class="chart-point" data-type="stress" data-day="' + p.d + '" />';
    });

    // 7. 动态十字交互参考竖线
    svgContent += '<line id="chartCursorLine" x1="0" y1="' + padT + '" x2="0" y2="' + (padT + plotH) + '" stroke="var(--color-gold)" stroke-width="1" stroke-dasharray="3 3" opacity="0" style="transition:opacity 0.15s ease;" />';

    svg.innerHTML = svgContent;

    // 8. 绑定鼠标悬浮交互（Tooltip 与 Cursor Line）
    var wrapper = $('trendChartSvgWrapper');
    var tooltip = $('trendChartTooltip');
    var cursorLine = $('chartCursorLine');

    if (wrapper && tooltip) {
      wrapper.onmousemove = function(e) {
        var rect = wrapper.getBoundingClientRect();
        var mouseX = e.clientX - rect.left;
        var svgX = (mouseX / rect.width) * W;

        if (svgX < padL || svgX > padL + plotW) {
          if (tooltip) tooltip.style.display = 'none';
          if (cursorLine) cursorLine.style.opacity = '0';
          return;
        }

        // 计算最接近的日期
        var targetDay = Math.round(1 + ((svgX - padL) / plotW) * (daysInMonth - 1));
        targetDay = Math.max(1, Math.min(daysInMonth, targetDay));
        var snappedX = getX(targetDay);

        if (cursorLine) {
          cursorLine.setAttribute('x1', snappedX.toFixed(1));
          cursorLine.setAttribute('x2', snappedX.toFixed(1));
          cursorLine.style.opacity = '0.65';
        }

        var rec = dayRecords[targetDay];
        var dateFullStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(targetDay).padStart(2, '0');

        var tipHtml = '';
        if (rec) {
          var eMeta = getEnergyMeta(rec.energy);
          var sMeta = getStressMeta(rec.stress);
          tipHtml += '<div style="font-weight:600;margin-bottom:5px;border-bottom:1px solid rgba(255,255,255,0.2);padding-bottom:3px;display:flex;justify-content:space-between;gap:8px;">';
          tipHtml += '<span>' + dateFullStr + '</span><span style="color:#C8E6C9;font-size:11px;">【今日日结】</span>';
          tipHtml += '</div>';
          tipHtml += '<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">';
          tipHtml += '<span style="color:#81C784;">●</span> 精力状态：<strong>' + rec.energy + ' / 10 · ' + eMeta.text + '</strong>';
          tipHtml += '</div>';
          tipHtml += '<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">';
          tipHtml += '<span style="color:#FF8A80;">●</span> 主观压力：<strong>' + rec.stress + ' / 10 · ' + sMeta.text + '</strong>';
          tipHtml += '</div>';
          if (rec.note) {
            tipHtml += '<div style="font-size:11px;color:#E0E0E0;margin-top:4px;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">心语：' + esc(rec.note) + '</div>';
          }
          if (rec.hasJournal) {
            tipHtml += '<div style="font-size:11px;color:#FFE082;margin-top:3px;">✨ 已写 AI 心事日记</div>';
          }
        } else {
          // 未打卡日期（平滑插值过渡段）
          tipHtml += '<div style="font-weight:600;margin-bottom:4px;border-bottom:1px solid rgba(255,255,255,0.2);padding-bottom:3px;display:flex;justify-content:space-between;gap:8px;">';
          tipHtml += '<span>' + dateFullStr + '</span><span style="color:#BDBDBD;font-size:11px;">【无日记 · 虚线过渡】</span>';
          tipHtml += '</div>';
          tipHtml += '<div style="font-size:11.5px;color:#E0E0E0;margin:2px 0;">此日未作心境日结，前后心境由平滑虚线连通。</div>';
        }

        tooltip.innerHTML = tipHtml;
        tooltip.style.display = 'block';
        tooltip.style.opacity = '1';

        // 浮窗定位
        var tipLeft = (snappedX / W) * rect.width + 12;
        if (tipLeft + 220 > rect.width) {
          tipLeft = (snappedX / W) * rect.width - 230;
        }
        tooltip.style.left = Math.max(8, tipLeft) + 'px';
        tooltip.style.top = '28px';
      };

      wrapper.onmouseleave = function() {
        if (tooltip) tooltip.style.display = 'none';
        if (cursorLine) cursorLine.style.opacity = '0';
      };
    }
  }

  function renderMiniCalendar()"""
    content = content[:p_js2.start()] + new_js_render_growth + content[p_js2.end():]

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("[ok] Patched frontend/_template.html successfully!")

if __name__ == "__main__":
    main()
