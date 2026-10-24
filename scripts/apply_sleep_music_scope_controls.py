# -*- coding: utf-8 -*-
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 更新 CSS 样式：添加 .sleep-palette-dot-auto 和相关变量
old_css_anchor = """.sleep-palette-dot-custom {
  background: conic-gradient(#F87171, #FBBF24, #34D399, #60A5FA, #A78BFA, #F472B6, #F87171);
}"""

new_css = """.sleep-palette-dot-custom {
  background: conic-gradient(#F87171, #FBBF24, #34D399, #60A5FA, #A78BFA, #F472B6, #F87171);
}
.sleep-palette-dot-auto {
  background: rgba(255, 255, 255, 0.12);
  color: #DCEBE1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: inherit;
  font-weight: 600;
}
.sleep-palette-dot-auto:hover {
  background: rgba(255, 255, 255, 0.25);
  color: #FFFFFF;
}
.sleep-palette-dot-auto.is-active {
  border: 2px solid #FFFFFF;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
}"""

if old_css_anchor in content and ".sleep-palette-dot-auto" not in content:
    content = content.replace(old_css_anchor, new_css)
    print("[ok] Updated CSS with .sleep-palette-dot-auto")
else:
    print("[-] CSS anchor already updated or not found")

# 2. 更新 HTML 结构 (移除曲目文字，增加上一曲/下一曲，静音按钮，隐藏原生复选框，增加律字自适应色块)
old_html = """          <!-- 示波器内置音乐播放控制条 (纯音乐控件按钮效果，无冗余文字标签) -->
          <div class="sleep-scope-controls" id="sleepScopeControls" aria-label="助眠音乐控制条">
            <div class="sleep-ctrl-group main-playback">
              <button type="button" class="sleep-ctrl-btn sleep-btn-play" id="sleepMusicToggle" aria-label="播放音乐" title="播放 / 暂停助眠音乐" aria-pressed="false">
                <svg class="sleep-icon-play" viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><polygon points="7 4 19 12 7 20 7 4"></polygon></svg>
                <svg class="sleep-icon-pause" viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
              </button>
              <button type="button" class="sleep-ctrl-btn" id="sleepMusicPanel" aria-label="曲库面板" title="打开曲库面板">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>
              </button>
              <div class="sleep-ctrl-item" title="切换助眠曲目">
                <label for="sleepTrackSelect" class="sr-only">曲目</label>
                <select id="sleepTrackSelect" class="sleep-scope-select">
                  <option value="0">行云流水</option>
                  <option value="1">禅境冥想</option>
                  <option value="2">秋雨箏韻</option>
                  <option value="3">秋雨琴簫合奏</option>
                  <option value="4">枕畔温煦</option>
                  <option value="5">空灵入梦</option>
                  <option value="6">夜幕归宁</option>
                  <option value="7">海潮摇篮</option>
                  <option value="8">眠琴微语</option>
                </select>
              </div>
            </div>

            <div class="sleep-ctrl-group secondary-playback">
              <div class="sleep-ctrl-item" title="音量调节">
                <label for="sleepVolume" class="sleep-ctrl-label-icon" title="音量" aria-label="音量">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
                </label>
                <input id="sleepVolume" type="range" min="0" max="100" value="25" aria-label="睡前音乐音量" class="sleep-scope-slider">
              </div>

              <div class="sleep-ctrl-item" title="定时关闭">
                <label for="sleepTimer" class="sleep-ctrl-label-icon" title="定时关闭" aria-label="定时关闭">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                </label>
                <select id="sleepTimer" class="sleep-scope-select" aria-label="定时关闭">
                  <option value="0">关闭</option>
                  <option value="5">5 分钟</option>
                  <option value="10">10 分钟</option>
                  <option value="20">20 分钟</option>
                  <option value="30">30 分钟</option>
                </select>
              </div>

              <label class="sleep-ctrl-btn sleep-fade-toggle is-active" id="sleepFadeLabel" title="定时结束声音平滑渐弱" aria-label="定时渐弱">
                <input type="checkbox" id="sleepFade" checked class="sr-only">
                <svg class="sleep-fade-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 10v4"></path><path d="M6 7v10"></path><path d="M10 4v16"></path><path d="M14 6v12"></path><path d="M18 9v6"></path><path d="M22 11v2"></path></svg>
              </label>

              <!-- 波形配色切换 -->
              <div class="sleep-ctrl-item sleep-color-picker-wrap">
                <button type="button" class="sleep-ctrl-btn" id="sleepWaveColorBtn" aria-label="更改波形色彩" title="更改波形色彩">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"></circle><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"></circle><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"></circle><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"></path></svg>
                </button>
                <input type="color" id="sleepWaveColorPicker" value="#85E3B3" class="sleep-color-native-input" title="自定义波形色彩" aria-label="自定义波形色彩">
                <div class="sleep-color-palette-pop" id="sleepColorPalettePop">
                  <button type="button" class="sleep-palette-dot is-active" data-color="#85E3B3" title="翡翠碧水 (默认)" style="background:#85E3B3;color:#85E3B3;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#E0C07A" title="琥珀暖金" style="background:#E0C07A;color:#E0C07A;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#B39DDB" title="紫藤夜梦" style="background:#B39DDB;color:#B39DDB;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#4DD0E1" title="沧海澄澜" style="background:#4DD0E1;color:#4DD0E1;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#F4A261" title="晚霞温煦" style="background:#F4A261;color:#F4A261;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#E8D7B8" title="水墨月白" style="background:#E8D7B8;color:#E8D7B8;"></button>
                  <button type="button" class="sleep-palette-dot sleep-palette-dot-custom" id="sleepCustomColorTrigger" title="自定义颜色" style="color:#FFF;"></button>
                </div>
              </div>
            </div>
          </div>"""

new_html = """          <!-- 示波器内置音乐播放控制条 (纯音乐控件按钮效果，无冗余文字标签) -->
          <div class="sleep-scope-controls" id="sleepScopeControls" aria-label="助眠音乐控制条">
            <div class="sleep-ctrl-group main-playback">
              <button type="button" class="sleep-ctrl-btn" id="sleepTrackPrev" aria-label="上一曲" title="上一曲">
                <svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
              </button>
              <button type="button" class="sleep-ctrl-btn sleep-btn-play" id="sleepMusicToggle" aria-label="播放音乐" title="播放 / 暂停助眠音乐" aria-pressed="false">
                <svg class="sleep-icon-play" viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><polygon points="7 4 19 12 7 20 7 4"></polygon></svg>
                <svg class="sleep-icon-pause" viewBox="0 0 24 24" width="15" height="15" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
              </button>
              <button type="button" class="sleep-ctrl-btn" id="sleepTrackNext" aria-label="下一曲" title="下一曲">
                <svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
              </button>
              <button type="button" class="sleep-ctrl-btn" id="sleepMusicPanel" aria-label="曲库面板" title="打开曲库面板">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>
              </button>
              <div class="sleep-ctrl-item" title="切换助眠曲目">
                <select id="sleepTrackSelect" class="sleep-scope-select" aria-label="切换助眠曲目">
                  <option value="0">行云流水</option>
                  <option value="1">禅境冥想</option>
                  <option value="2">秋雨箏韻</option>
                  <option value="3">秋雨琴簫合奏</option>
                  <option value="4">枕畔温煦</option>
                  <option value="5">空灵入梦</option>
                  <option value="6">夜幕归宁</option>
                  <option value="7">海潮摇篮</option>
                  <option value="8">眠琴微语</option>
                </select>
              </div>
            </div>

            <div class="sleep-ctrl-group secondary-playback">
              <div class="sleep-ctrl-item" title="音量调节">
                <button type="button" class="sleep-ctrl-label-icon" id="sleepVolumeBtn" title="静音 / 恢复音量" aria-label="音量" style="background:none;border:none;cursor:pointer;">
                  <svg id="sleepVolumeSvg" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>
                </button>
                <input id="sleepVolume" type="range" min="0" max="100" value="25" aria-label="睡前音乐音量" class="sleep-scope-slider">
              </div>

              <div class="sleep-ctrl-item" title="定时关闭">
                <span class="sleep-ctrl-label-icon" title="定时关闭" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                </span>
                <select id="sleepTimer" class="sleep-scope-select" aria-label="定时关闭">
                  <option value="0">∞</option>
                  <option value="5">5′</option>
                  <option value="10">10′</option>
                  <option value="20">20′</option>
                  <option value="30">30′</option>
                </select>
              </div>

              <label class="sleep-ctrl-btn sleep-fade-toggle is-active" id="sleepFadeLabel" title="定时结束声音平滑渐弱" aria-label="定时渐弱">
                <input type="checkbox" id="sleepFade" checked style="position:absolute;opacity:0;pointer-events:none;width:0;height:0;">
                <svg class="sleep-fade-icon" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 10v4"></path><path d="M6 7v10"></path><path d="M10 4v16"></path><path d="M14 6v12"></path><path d="M18 9v6"></path><path d="M22 11v2"></path></svg>
              </label>

              <!-- 波形配色切换 -->
              <div class="sleep-ctrl-item sleep-color-picker-wrap">
                <button type="button" class="sleep-ctrl-btn" id="sleepWaveColorBtn" aria-label="更改波形色彩" title="更改波形色彩">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"></circle><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"></circle><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"></circle><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"></path></svg>
                </button>
                <input type="color" id="sleepWaveColorPicker" value="#85E3B3" class="sleep-color-native-input" title="自定义波形色彩" aria-label="自定义波形色彩">
                <div class="sleep-color-palette-pop" id="sleepColorPalettePop">
                  <button type="button" class="sleep-palette-dot is-active" data-color="#85E3B3" title="翡翠碧水 (默认)" style="background:#85E3B3;color:#85E3B3;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#E0C07A" title="琥珀暖金" style="background:#E0C07A;color:#E0C07A;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#B39DDB" title="紫藤夜梦" style="background:#B39DDB;color:#B39DDB;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#4DD0E1" title="沧海澄澜" style="background:#4DD0E1;color:#4DD0E1;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#F4A261" title="晚霞温煦" style="background:#F4A261;color:#F4A261;"></button>
                  <button type="button" class="sleep-palette-dot" data-color="#E8D7B8" title="水墨月白" style="background:#E8D7B8;color:#E8D7B8;"></button>
                  <button type="button" class="sleep-palette-dot sleep-palette-dot-custom" id="sleepCustomColorTrigger" title="自定义颜色" style="color:#FFF;"></button>
                  <button type="button" class="sleep-palette-dot sleep-palette-dot-auto" id="sleepAutoColorBtn" title="跟随曲目自动色彩" aria-label="跟随曲目自动色彩"><span style="font-size:10px;line-height:1;display:block;">律</span></button>
                </div>
              </div>
            </div>
          </div>"""

if old_html in content:
    content = content.replace(old_html, new_html)
    print("[ok] Updated HTML structure inside .sleep-scope-wrap")
else:
    print("[x] Could not find old_html in template")

# 3. 更新 initSleepGuide 中的 JS 监听（Prev, Next, Volume mute/unmute）
old_init_js = """    $('sleepStop').addEventListener('click', sleepExit);
    $('sleepMusicToggle').addEventListener('click', sleepToggleMusic);
    $('sleepMusicPanel').addEventListener('click', function(event) { bgmEngine.togglePanel(event); });
    $('sleepTrackSelect').addEventListener('change', function() {"""

new_init_js = """    $('sleepStop').addEventListener('click', sleepExit);
    $('sleepMusicToggle').addEventListener('click', sleepToggleMusic);
    $('sleepMusicPanel').addEventListener('click', function(event) { bgmEngine.togglePanel(event); });

    // Prev / Next 切歌控制
    var prevBtn = $('sleepTrackPrev');
    var nextBtn = $('sleepTrackNext');
    if (prevBtn) {
      prevBtn.addEventListener('click', function(e) {
        e.preventDefault(); e.stopPropagation();
        var sel = $('sleepTrackSelect');
        if (!sel) return;
        var idx = (parseInt(sel.value, 10) || 0) - 1;
        if (idx < 0) idx = sel.options.length - 1;
        sel.value = String(idx);
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', function(e) {
        e.preventDefault(); e.stopPropagation();
        var sel = $('sleepTrackSelect');
        if (!sel) return;
        var idx = (parseInt(sel.value, 10) || 0) + 1;
        if (idx >= sel.options.length) idx = 0;
        sel.value = String(idx);
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      });
    }

    // 音量静音与恢复控制
    var volBtn = $('sleepVolumeBtn');
    if (volBtn) {
      volBtn.addEventListener('click', function(e) {
        e.preventDefault(); e.stopPropagation();
        var volSlider = $('sleepVolume');
        if (!volSlider) return;
        var cur = parseInt(volSlider.value, 10) || 0;
        if (cur > 0) {
          volSlider.dataset.prevVol = String(cur);
          volSlider.value = '0';
        } else {
          volSlider.value = volSlider.dataset.prevVol || '25';
        }
        volSlider.dispatchEvent(new Event('input', { bubbles: true }));
      });
    }

    $('sleepTrackSelect').addEventListener('change', function() {"""

if old_init_js in content:
    content = content.replace(old_init_js, new_init_js)
    print("[ok] Updated initSleepGuide JS listeners")
else:
    print("[x] Could not find old_init_js")

# 4. 更新 sleepOscilloscope 内部色彩逻辑和弹窗事件
old_scope_header = """  var sleepOscilloscope = (function() {
    var canvas, ctx, wrap;
    var ledEl, titleEl, breathTextEl, statusEl;
    var animId = null;
    var currentAmp = 3.2;
    var phase1 = 0, phase2 = 0, phase3 = 0;
    var isInitialized = false;

    var SCOPE_TRACKS = ["""

new_scope_header = """  var sleepOscilloscope = (function() {
    var canvas, ctx, wrap;
    var ledEl, titleEl, breathTextEl, statusEl;
    var animId = null;
    var currentAmp = 3.2;
    var phase1 = 0, phase2 = 0, phase3 = 0;
    var isInitialized = false;

    var customWaveColor = null;
    try {
      customWaveColor = localStorage.getItem('wutang_sleep_wave_color') || null;
    } catch(e) {}

    function hexToRgb(hex) {
      var c = hex.replace('#', '');
      if (c.length === 3) c = c[0] + c[0] + c[1] + c[1] + c[2] + c[2];
      var num = parseInt(c, 16);
      return {
        r: (num >> 16) & 255,
        g: (num >> 8) & 255,
        b: num & 255
      };
    }

    function hexToTheme(hex) {
      var rgb = hexToRgb(hex);
      var secR = Math.max(0, Math.floor(rgb.r * 0.72));
      var secG = Math.max(0, Math.floor(rgb.g * 0.72));
      var secB = Math.max(0, Math.floor(rgb.b * 0.72));
      return {
        stroke: hex,
        secondary: 'rgb(' + secR + ',' + secG + ',' + secB + ')',
        aura: 'rgba(' + rgb.r + ', ' + rgb.g + ', ' + rgb.b + ', '
      };
    }

    function updateColorDotsUI() {
      var dots = document.querySelectorAll('.sleep-palette-dot');
      dots.forEach(function(dot) {
        if (dot.id === 'sleepCustomColorTrigger' || dot.id === 'sleepAutoColorBtn') return;
        var dotColor = dot.getAttribute('data-color');
        if (customWaveColor && dotColor && dotColor.toLowerCase() === customWaveColor.toLowerCase()) {
          dot.classList.add('is-active');
        } else {
          dot.classList.remove('is-active');
        }
      });
      var autoBtn = $('sleepAutoColorBtn');
      if (autoBtn) {
        if (!customWaveColor) autoBtn.classList.add('is-active');
        else autoBtn.classList.remove('is-active');
      }
      var customTrigger = $('sleepCustomColorTrigger');
      if (customTrigger) {
        var isPreset = false;
        dots.forEach(function(d) {
          if (d.getAttribute('data-color') && customWaveColor && d.getAttribute('data-color').toLowerCase() === customWaveColor.toLowerCase()) isPreset = true;
        });
        if (customWaveColor && !isPreset) customTrigger.classList.add('is-active');
        else customTrigger.classList.remove('is-active');
      }
      var picker = $('sleepWaveColorPicker');
      if (picker && customWaveColor) picker.value = customWaveColor;
      
      var effectiveStroke = customWaveColor || (SCOPE_TRACKS[0] ? SCOPE_TRACKS[0].stroke : '#85E3B3');
      if (wrap) {
        wrap.style.setProperty('--scope-accent', effectiveStroke);
        wrap.style.setProperty('--scope-accent-glow', effectiveStroke + '66');
      }
    }

    function setWaveColor(colorHex, save) {
      if (colorHex) {
        customWaveColor = colorHex;
        if (save) {
          try { localStorage.setItem('wutang_sleep_wave_color', colorHex); } catch(e) {}
        }
      } else {
        customWaveColor = null;
        if (save) {
          try { localStorage.removeItem('wutang_sleep_wave_color'); } catch(e) {}
        }
      }
      updateColorDotsUI();
    }

    var SCOPE_TRACKS = ["""

if old_scope_header in content:
    content = content.replace(old_scope_header, new_scope_header)
    print("[ok] Updated sleepOscilloscope header with color functions")
else:
    print("[x] Could not find old_scope_header")

# 5. 更新 render 中的 theme
old_render_theme = """      var trackIdx = 0;
      if ($('sleepTrackSelect')) {
        trackIdx = parseInt($('sleepTrackSelect').value, 10) || 0;
      }
      if (trackIdx < 0 || trackIdx >= SCOPE_TRACKS.length) trackIdx = 0;
      var theme = SCOPE_TRACKS[trackIdx];"""

new_render_theme = """      var trackIdx = 0;
      if ($('sleepTrackSelect')) {
        trackIdx = parseInt($('sleepTrackSelect').value, 10) || 0;
      }
      if (trackIdx < 0 || trackIdx >= SCOPE_TRACKS.length) trackIdx = 0;
      var theme = SCOPE_TRACKS[trackIdx];

      if (customWaveColor) {
        var customTheme = hexToTheme(customWaveColor);
        theme = {
          name: theme.name,
          stroke: customTheme.stroke,
          secondary: customTheme.secondary,
          aura: customTheme.aura,
          status: theme.status,
          h1: theme.h1,
          h2: theme.h2,
          h3: theme.h3
        };
      }
      if (wrap) {
        wrap.style.setProperty('--scope-accent', theme.stroke);
        wrap.style.setProperty('--scope-accent-glow', theme.stroke + '66');
      }"""

if old_render_theme in content:
    content = content.replace(old_render_theme, new_render_theme)
    print("[ok] Updated sleepOscilloscope.render theme with customWaveColor")
else:
    print("[x] Could not find old_render_theme")

# 6. 更新 init() 中的弹窗与色块监听以及防冒泡
old_init_body = """      // 点击示波器切换播放
      wrap.addEventListener('click', function(e) {
        e.preventDefault();
        sleepToggleMusic();
      });"""

new_init_body = """      // 颜色选择器弹窗与色块监听
      var colorBtn = $('sleepWaveColorBtn');
      var palettePop = $('sleepColorPalettePop');
      if (colorBtn && palettePop) {
        colorBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          palettePop.classList.toggle('is-open');
        });
        document.addEventListener('click', function(e) {
          if (!e.target.closest('.sleep-color-picker-wrap')) {
            palettePop.classList.remove('is-open');
          }
        });
      }

      document.querySelectorAll('.sleep-palette-dot').forEach(function(dot) {
        if (dot.id === 'sleepCustomColorTrigger' || dot.id === 'sleepAutoColorBtn') return;
        dot.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          var col = dot.getAttribute('data-color');
          setWaveColor(col, true);
        });
      });

      var customTrigger = $('sleepCustomColorTrigger');
      var colorInput = $('sleepWaveColorPicker');
      if (customTrigger && colorInput) {
        customTrigger.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          colorInput.click();
        });
        colorInput.addEventListener('input', function(e) {
          e.stopPropagation();
          setWaveColor(this.value, true);
        });
        colorInput.addEventListener('change', function(e) {
          e.stopPropagation();
          setWaveColor(this.value, true);
        });
      }

      var autoColorBtn = $('sleepAutoColorBtn');
      if (autoColorBtn) {
        autoColorBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          setWaveColor(null, true);
        });
      }

      // 初始化色彩指示
      updateColorDotsUI();

      // 点击示波器切换播放 (排除控件栏与色彩弹窗)
      wrap.addEventListener('click', function(e) {
        if (e.target.closest('#sleepScopeControls, .sleep-color-palette-pop')) {
          return;
        }
        e.preventDefault();
        sleepToggleMusic();
      });"""

if old_init_body in content:
    content = content.replace(old_init_body, new_init_body)
    print("[ok] Updated sleepOscilloscope.init with color listeners and safe click handler")
else:
    print("[x] Could not find old_init_body")

# 7. 更新 sleepOscilloscope 返回接口
old_scope_return = """    return {
      init: init,
      start: startLoop,
      stop: stopLoop
    };"""

new_scope_return = """    return {
      init: init,
      start: startLoop,
      stop: stopLoop,
      setColor: setWaveColor,
      getColor: function() { return customWaveColor; }
    };"""

if old_scope_return in content:
    content = content.replace(old_scope_return, new_scope_return)
    print("[ok] Updated sleepOscilloscope return methods (setColor, getColor)")
else:
    print("[x] Could not find old_scope_return")

with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("[SUCCESS] _template.html patch complete.")
