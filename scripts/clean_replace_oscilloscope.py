# -*- coding: utf-8 -*-
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 替换 HTML 中的自适应色块中的 "律" 为纯 SVG 循环图标
old_dot = """<button type="button" class="sleep-palette-dot sleep-palette-dot-auto" id="sleepAutoColorBtn" title="跟随曲目自动色彩" aria-label="跟随曲目自动色彩"><span style="font-size:10px;line-height:1;display:block;">律</span></button>"""
new_dot = """<button type="button" class="sleep-palette-dot sleep-palette-dot-auto" id="sleepAutoColorBtn" title="跟随曲目自动色彩" aria-label="跟随曲目自动色彩"><svg viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M21.5 2v6h-6"></path><path d="M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path></svg></button>"""

if old_dot in content:
    content = content.replace(old_dot, new_dot)

start_marker = "  /* ==========================================================================\n     助眠音乐呼吸示波器 (Sleep Music Breathing Oscilloscope)\n     ========================================================================== */\n  var sleepOscilloscope = (function() {"
if start_marker not in content:
    start_marker = "  /* ==========================================================================\r\n     助眠音乐呼吸示波器 (Sleep Music Breathing Oscilloscope)\r\n     ========================================================================== */\r\n  var sleepOscilloscope = (function() {"

end_marker = "  function switchWellbeingTab(tab) {"

if start_marker not in content or end_marker not in content:
    raise SystemExit("[x] Could not find markers for sleepOscilloscope in _template.html")

prefix = content[:content.find(start_marker)]
suffix = content[content.find(end_marker):]

CLEAN_SLEEP_OSCILLOSCOPE = """  /* ==========================================================================
     助眠音乐呼吸示波器 (Sleep Music Breathing Oscilloscope)
     ========================================================================== */
  var sleepOscilloscope = (function() {
    var canvas, ctx, wrap;
    var ledEl, titleEl, breathTextEl, statusEl;
    var animId = null;
    var currentAmp = 3.2;
    var phase1 = 0, phase2 = 0, phase3 = 0;
    var isInitialized = false;
    var userColor = null;
    var activeStroke = null;
    var activeSecondary = null;
    var activeAura = null;

    function hexToRgb(hex) {
      if (!hex) return null;
      var clean = hex.replace('#', '').trim();
      if (clean.length === 3) {
        clean = clean[0] + clean[0] + clean[1] + clean[1] + clean[2] + clean[2];
      }
      var m = /^([a-f\\d]{2})([a-f\\d]{2})([a-f\\d]{2})$/i.exec(clean);
      return m ? {
        r: parseInt(m[1], 16),
        g: parseInt(m[2], 16),
        b: parseInt(m[3], 16)
      } : null;
    }

    function syncPaletteDots(selectedHex) {
      var dots = document.querySelectorAll('.sleep-palette-dot[data-color]');
      var matched = false;
      dots.forEach(function(dot) {
        var c = dot.getAttribute('data-color');
        if (c && selectedHex && c.toLowerCase() === selectedHex.toLowerCase()) {
          dot.classList.add('is-active');
          matched = true;
        } else {
          dot.classList.remove('is-active');
        }
      });
      var autoBtn = $('sleepAutoColorBtn');
      if (autoBtn) {
        if (!selectedHex) {
          autoBtn.classList.add('is-active');
        } else {
          autoBtn.classList.remove('is-active');
        }
      }
      var customTrigger = $('sleepCustomColorTrigger');
      if (customTrigger) {
        if (!matched && selectedHex) {
          customTrigger.classList.add('is-active');
          customTrigger.style.background = selectedHex;
        } else {
          customTrigger.classList.remove('is-active');
          customTrigger.style.background = '';
        }
      }
    }

    function applyWaveColor(hex) {
      if (!hex) {
        userColor = null;
        activeStroke = null;
        activeSecondary = null;
        activeAura = null;
        if (ledEl) {
          ledEl.style.backgroundColor = '';
          ledEl.style.boxShadow = '';
        }
        if (wrap) {
          var trackIdx = 0;
          if ($('sleepTrackSelect')) trackIdx = parseInt($('sleepTrackSelect').value, 10) || 0;
          var curTheme = SCOPE_TRACKS[trackIdx] || SCOPE_TRACKS[0];
          wrap.style.setProperty('--scope-accent', curTheme.stroke);
          wrap.style.setProperty('--scope-accent-glow', curTheme.aura + '0.45)');
        }
        return;
      }
      var rgb = hexToRgb(hex);
      if (!rgb) return;
      userColor = hex;
      activeStroke = hex;
      activeSecondary = 'rgba(' + Math.round(rgb.r * 0.72) + ', ' + Math.round(rgb.g * 0.72) + ', ' + Math.round(rgb.b * 0.72) + ', 0.85)';
      activeAura = 'rgba(' + rgb.r + ', ' + rgb.g + ', ' + rgb.b + ', ';
      if (ledEl) {
        ledEl.style.backgroundColor = hex;
        ledEl.style.boxShadow = '0 0 8px ' + hex + ', 0 0 16px ' + activeAura + '0.8)';
      }
      if (wrap) {
        wrap.style.setProperty('--scope-accent', hex);
        wrap.style.setProperty('--scope-accent-glow', activeAura + '0.45)');
      }
    }

    function chooseColor(hex) {
      applyWaveColor(hex);
      syncPaletteDots(hex);
      try {
        if (hex) {
          localStorage.setItem('wt_sleep_wave_color', hex);
        } else {
          localStorage.removeItem('wt_sleep_wave_color');
        }
      } catch (e) {}
    }

    var SCOPE_TRACKS = [
      {
        name: '行云流水',
        stroke: '#76D7B7',
        secondary: '#5C9E96',
        aura: 'rgba(118, 215, 183, ',
        status: '行云流水 · 如水润物，心念流转不滞',
        h1: 1.0, h2: 2.1, h3: 0.5
      },
      {
        name: '禅境冥想',
        stroke: '#E0C07A',
        secondary: '#C49B5B',
        aura: 'rgba(224, 192, 122, ',
        status: '禅境冥想 · 虚室生白，凝神入定安然',
        h1: 0.75, h2: 1.5, h3: 0.6
      },
      {
        name: '秋雨箏韻',
        stroke: '#85E3B3',
        secondary: '#587C65',
        aura: 'rgba(133, 227, 179, ',
        status: '秋雨箏韻 · 筝声如雨，涤荡心尘渐远',
        h1: 1.25, h2: 2.7, h3: 0.4
      },
      {
        name: '秋雨琴簫合奏',
        stroke: '#A8E6CF',
        secondary: '#7E6B5A',
        aura: 'rgba(168, 230, 207, ',
        status: '秋雨琴簫合奏 · 琴箫和鸣，万籁自息入梦',
        h1: 0.88, h2: 1.76, h3: 0.52
      },
      {
        name: '枕畔温煦',
        stroke: '#F4A261',
        secondary: '#E76F51',
        aura: 'rgba(244, 162, 97, ',
        status: '枕畔温煦 · 暖意入怀，倦意舒展渐浓',
        h1: 0.85, h2: 1.6, h3: 0.45
      },
      {
        name: '空灵入梦',
        stroke: '#B39DDB',
        secondary: '#7E57C2',
        aura: 'rgba(179, 157, 219, ',
        status: '空灵入梦 · 空灵悠远，随风轻飏入梦',
        h1: 0.65, h2: 1.3, h3: 0.55
      },
      {
        name: '夜幕归宁',
        stroke: '#64B5F6',
        secondary: '#42A5F5',
        aura: 'rgba(100, 181, 246, ',
        status: '夜幕归宁 · 夜幕轻垂，晚籁自安息心',
        h1: 0.92, h2: 1.84, h3: 0.48
      },
      {
        name: '海潮摇篮',
        stroke: '#4DD0E1',
        secondary: '#26A69A',
        aura: 'rgba(77, 208, 225, ',
        status: '海潮摇篮 · 潮涌如息，枕浪安澜入眠',
        h1: 0.72, h2: 1.44, h3: 0.38
      },
      {
        name: '眠琴微语',
        stroke: '#E8D7B8',
        secondary: '#D4B896',
        aura: 'rgba(232, 215, 184, ',
        status: '眠琴微语 · 琴音轻抚，心绪归平渐恬',
        h1: 1.15, h2: 2.3, h3: 0.6
      }
    ];

    // 漂浮微光微粒 (Drifting Zen Dewdrop Particles)
    var particles = [];
    for (var i = 0; i < 14; i++) {
      particles.push({
        x: Math.random(),
        speed: 0.0003 + Math.random() * 0.0006,
        size: 0.8 + Math.random() * 1.5,
        alpha: 0.25 + Math.random() * 0.55,
        phase: Math.random() * Math.PI * 2
      });
    }

    function isVisible() {
      if (document.hidden) return false;
      if (typeof appState !== 'undefined' && appState.mainTab && appState.mainTab !== 'wellbeing') return false;
      if (typeof appState !== 'undefined' && appState.wellbeingTab && appState.wellbeingTab !== 'sleep') return false;
      var sec = $('sleepHomeSection');
      if (!sec || sec.offsetParent === null) return false;
      var wbArea = $('wellbeingArea');
      if (wbArea && wbArea.classList.contains('hidden')) return false;
      return true;
    }

    function render(now) {
      if (!canvas || !ctx) return;

      var rect = canvas.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) {
        if (animId) animId = requestAnimationFrame(render);
        return;
      }

      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var targetW = Math.round(rect.width * dpr);
      var targetH = Math.round(rect.height * dpr);
      if (canvas.width !== targetW || canvas.height !== targetH) {
        canvas.width = targetW;
        canvas.height = targetH;
      }

      var w = canvas.width;
      var h = canvas.height;
      var midX = w / 2;
      var midY = h / 2;

      // 状态判断：优先检查睡前音乐是否开启
      var isSleepStarted = (typeof sleepGuideState !== 'undefined' && sleepGuideState.musicStartedHere);
      var isBgmPlaying = (typeof bgmEngine !== 'undefined' && bgmEngine.getState().isPlaying);
      var isPlaying = isSleepStarted || isBgmPlaying;

      var trackIdx = 0;
      if ($('sleepTrackSelect')) {
        trackIdx = parseInt($('sleepTrackSelect').value, 10) || 0;
      }
      if (trackIdx < 0 || trackIdx >= SCOPE_TRACKS.length) trackIdx = 0;
      var theme = SCOPE_TRACKS[trackIdx];

      var waveStroke = activeStroke || theme.stroke;
      var waveSec = activeSecondary || theme.secondary;
      var waveAura = activeAura || theme.aura;

      if (wrap) {
        wrap.style.setProperty('--scope-accent', waveStroke);
        wrap.style.setProperty('--scope-accent-glow', waveAura + '0.45)');
      }

      // 呼吸节律：5.6s 完整自然呼吸周期
      var breathCycle = 5600;
      var breathPhase = ((now % breathCycle) / breathCycle) * (2 * Math.PI);
      var breathSine = Math.sin(breathPhase - Math.PI / 2); // -1 (呼末) 到 +1 (吸顶)
      var breathVal = 0.5 + 0.5 * breathSine; // 0 到 1
      var breathAmp = 0.65 + 0.35 * breathVal;

      // 振幅平滑插值
      var vol = 0.25;
      if ($('sleepVolume')) {
        vol = (parseInt($('sleepVolume').value, 10) || 25) / 100;
      }
      var targetAmp = 3.2;
      if (isPlaying) {
        targetAmp = (10 + vol * 26) * dpr;
      } else {
        targetAmp = 3.2 * dpr;
      }
      currentAmp += (targetAmp - currentAmp) * 0.08;

      // 相位推进
      var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (!reduced) {
        var speedMul = isPlaying ? (1.0 + vol * 0.6) : 0.45;
        phase1 += 0.022 * speedMul;
        phase2 += 0.016 * speedMul;
        phase3 += 0.012 * speedMul;
      }

      // UI 文本与状态同步
      if (wrap) {
        if (isPlaying) {
          if (!wrap.classList.contains('is-playing')) wrap.classList.add('is-playing');
        } else {
          if (wrap.classList.contains('is-playing')) wrap.classList.remove('is-playing');
        }
      }

      if (titleEl) {
        titleEl.textContent = isPlaying ? (theme.name + ' · 助眠声波') : '助眠声波 · 随息安澜';
      }

      if (breathTextEl) {
        if (isPlaying) {
          if (breathSine > 0.08) {
            breathTextEl.innerHTML = '<span style="color:' + waveStroke + '">▲</span> 吸气 · 身心充盈';
          } else if (breathSine < -0.08) {
            breathTextEl.innerHTML = '<span style="color:#71836E">▼</span> 呼气 · 缓缓释压';
          } else {
            breathTextEl.innerHTML = '<span style="color:' + waveStroke + '">●</span> 随息 · 安然流转';
          }
        } else {
          breathTextEl.innerHTML = '<span style="opacity:0.6">○</span> 静息态 · 待播放';
        }
      }

      if (statusEl) {
        statusEl.textContent = isPlaying ? theme.status : '微澜初起 · 呼吸保持自然，不屏息、不规定次数';
      }

      // 1. 清空画布并绘制深色夜砚底色
      ctx.fillStyle = '#0D1612';
      ctx.fillRect(0, 0, w, h);

      // 2. 呼吸柔光晕 (Breathing Radial Aura)
      var auraAlpha = (isPlaying ? 0.25 : 0.08) * (0.6 + 0.4 * breathVal);
      var radGrad = ctx.createRadialGradient(midX, midY, 6 * dpr, midX, midY, w * 0.52);
      radGrad.addColorStop(0, waveAura + auraAlpha + ')');
      radGrad.addColorStop(0.55, waveAura + (auraAlpha * 0.35) + ')');
      radGrad.addColorStop(1, 'rgba(13, 22, 18, 0)');
      ctx.fillStyle = radGrad;
      ctx.fillRect(0, 0, w, h);

      // 3. 示波器坐标网格与基准标尺 (Oscilloscope Reticle & Grid)
      ctx.save();
      // 水平基线 (0V Baseline)
      ctx.beginPath();
      ctx.setLineDash([4 * dpr, 6 * dpr]);
      ctx.strokeStyle = 'rgba(113, 131, 110, 0.22)';
      ctx.lineWidth = 1 * dpr;
      ctx.moveTo(0, midY);
      ctx.lineTo(w, midY);
      ctx.stroke();

      // 水平辅助线 (±22px)
      ctx.beginPath();
      ctx.setLineDash([2 * dpr, 8 * dpr]);
      ctx.strokeStyle = 'rgba(113, 131, 110, 0.08)';
      var offsetGrid = 22 * dpr;
      ctx.moveTo(0, midY - offsetGrid); ctx.lineTo(w, midY - offsetGrid);
      ctx.moveTo(0, midY + offsetGrid); ctx.lineTo(w, midY + offsetGrid);
      ctx.stroke();

      // 垂直刻度点 (Tick marks)
      ctx.setLineDash([]);
      ctx.strokeStyle = 'rgba(113, 131, 110, 0.28)';
      ctx.lineWidth = 1 * dpr;
      var tickStep = 45 * dpr;
      var tickStart = (midX % tickStep);
      for (var tx = tickStart; tx < w; tx += tickStep) {
        ctx.beginPath();
        ctx.moveTo(tx, midY - 3 * dpr);
        ctx.lineTo(tx, midY + 3 * dpr);
        ctx.stroke();
      }
      ctx.restore();

      // 4. 计算波形切片
      var points = [];
      var pointsSec = [];
      var numPoints = Math.min(180, Math.max(80, Math.floor(w / (2.5 * dpr))));
      for (var p = 0; p <= numPoints; p++) {
        var u = p / numPoints; // 0 to 1
        var px = u * w;
        // 汉宁/正弦开窗包络，让左右两端自然平缓归零
        var env = Math.pow(Math.sin(Math.PI * u), 0.82);

        // 主波形合成 (谐波 + 呼吸调制)
        var s1 = Math.sin(2 * Math.PI * theme.h1 * u * 2.8 - phase1);
        var s2 = Math.sin(2 * Math.PI * theme.h2 * u * 2.8 + phase2);
        var yMain = midY + env * (currentAmp * breathAmp) * (0.72 * s1 + 0.28 * s2);
        points.push({ x: px, y: yMain });

        // 副和弦波 (Ambient Harmonic Echo)
        var s3 = Math.sin(2 * Math.PI * theme.h3 * u * 2.8 + phase3);
        var s4 = Math.cos(2 * Math.PI * theme.h1 * 1.5 * u * 2.8 - phase1 * 0.7);
        var ySec = midY + env * (currentAmp * 0.58 * (0.7 + 0.3 * breathVal)) * (0.65 * s3 + 0.35 * s4);
        pointsSec.push({ x: px, y: ySec });
      }

      // 5. 柔和水墨光晕层 (Soft Ambient Wash under main wave)
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(points[0].x, midY);
      for (var n = 0; n < points.length; n++) {
        ctx.lineTo(points[n].x, points[n].y);
      }
      ctx.lineTo(points[points.length - 1].x, midY);
      ctx.closePath();
      var washGrad = ctx.createLinearGradient(0, midY - currentAmp, 0, midY + currentAmp);
      washGrad.addColorStop(0, waveAura + (isPlaying ? (0.16 * breathVal) : 0.04) + ')');
      washGrad.addColorStop(0.5, waveAura + (isPlaying ? (0.08 * breathVal) : 0.02) + ')');
      washGrad.addColorStop(1, 'rgba(13, 22, 18, 0)');
      ctx.fillStyle = washGrad;
      ctx.fill();
      ctx.restore();

      // 6. 绘制副和弦波 (波形层 1 - 柔和金铜/墨绿谐波)
      ctx.save();
      ctx.beginPath();
      for (var j = 0; j < pointsSec.length; j++) {
        if (j === 0) ctx.moveTo(pointsSec[j].x, pointsSec[j].y);
        else ctx.lineTo(pointsSec[j].x, pointsSec[j].y);
      }
      ctx.strokeStyle = waveSec;
      ctx.lineWidth = 1.2 * dpr;
      ctx.shadowColor = waveSec;
      ctx.shadowBlur = 6 * dpr;
      ctx.globalAlpha = isPlaying ? 0.6 : 0.25;
      ctx.stroke();
      ctx.restore();

      // 7. 绘制主示波器波形 (波形层 2 - 荧光青碧主波)
      ctx.save();
      ctx.beginPath();
      for (var k = 0; k < points.length; k++) {
        if (k === 0) ctx.moveTo(points[k].x, points[k].y);
        else ctx.lineTo(points[k].x, points[k].y);
      }
      ctx.strokeStyle = waveStroke;
      ctx.lineWidth = (isPlaying ? 2.4 : 1.5) * dpr;
      ctx.shadowColor = waveStroke;
      ctx.shadowBlur = (isPlaying ? (12 + 6 * breathVal) : 5) * dpr;
      ctx.globalAlpha = isPlaying ? 0.95 : 0.65;
      ctx.stroke();
      ctx.restore();

      // 8. 绘制呼吸主扫描光斑 (Phosphor Sweep Beam Spot)
      if (isPlaying && !reduced) {
        var sweepU = ((now * 0.00018) % 1);
        var sweepIdx = Math.floor(sweepU * (points.length - 1));
        var pt = points[sweepIdx] || points[0];
        ctx.save();
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, (3.0 + 1.2 * breathVal) * dpr, 0, Math.PI * 2);
        ctx.fillStyle = '#FFFFFF';
        ctx.shadowColor = waveStroke;
        ctx.shadowBlur = 14 * dpr;
        ctx.fill();
        ctx.restore();
      }

      // 9. 漂浮微光微粒 (Ambient Dewdrops)
      ctx.save();
      for (var m = 0; m < particles.length; m++) {
        var pItem = particles[m];
        if (!reduced) {
          pItem.x += pItem.speed * (isPlaying ? 1.4 : 0.6);
          if (pItem.x > 1) pItem.x -= 1;
        }
        var pU = pItem.x;
        var pIdx = Math.floor(pU * (points.length - 1));
        var waveRefY = points[pIdx] ? points[pIdx].y : midY;
        var py = midY + (waveRefY - midY) * 0.65 + Math.sin(pItem.phase + now * 0.002) * (7 * dpr);
        var px = pU * w;

        ctx.beginPath();
        ctx.arc(px, py, pItem.size * dpr, 0, Math.PI * 2);
        ctx.fillStyle = waveStroke;
        ctx.shadowColor = waveStroke;
        ctx.shadowBlur = 5 * dpr;
        ctx.globalAlpha = pItem.alpha * (0.4 + 0.6 * breathVal) * (isPlaying ? 0.85 : 0.35);
        ctx.fill();
      }
      ctx.restore();

      // 下一帧
      animId = requestAnimationFrame(render);
    }

    function startLoop() {
      if (!animId) {
        animId = requestAnimationFrame(render);
      }
    }

    function stopLoop() {
      if (animId) {
        cancelAnimationFrame(animId);
        animId = null;
      }
    }

    function init() {
      wrap = $('sleepScopeWrap');
      canvas = $('sleepScopeCanvas');
      if (!wrap || !canvas || isInitialized) return;
      isInitialized = true;
      ctx = canvas.getContext('2d');

      ledEl = $('sleepScopeLed');
      titleEl = $('sleepScopeTrackTitle');
      breathTextEl = $('sleepScopeBreathText');
      statusEl = $('sleepScopeStatus');

      // 色彩选择与切换
      var colorBtn = $('sleepWaveColorBtn');
      var colorPop = $('sleepColorPalettePop');
      var nativePicker = $('sleepWaveColorPicker');
      var customTrigger = $('sleepCustomColorTrigger');
      var autoColorBtn = $('sleepAutoColorBtn');

      var savedColor = null;
      try {
        savedColor = localStorage.getItem('wt_sleep_wave_color');
      } catch (e) {}
      if (savedColor) {
        applyWaveColor(savedColor);
        if (nativePicker) nativePicker.value = savedColor;
        syncPaletteDots(savedColor);
      } else {
        syncPaletteDots(null);
      }

      if (colorBtn && colorPop) {
        colorBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          colorPop.classList.toggle('is-open');
        });

        document.querySelectorAll('.sleep-palette-dot[data-color]').forEach(function(dot) {
          dot.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var c = this.getAttribute('data-color');
            if (c) {
              chooseColor(c);
              if (nativePicker) nativePicker.value = c;
            }
            colorPop.classList.remove('is-open');
          });
        });

        if (autoColorBtn) {
          autoColorBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            chooseColor(null);
            colorPop.classList.remove('is-open');
          });
        }

        if (customTrigger && nativePicker) {
          customTrigger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            nativePicker.click();
          });
        }

        if (nativePicker) {
          nativePicker.addEventListener('input', function(e) {
            chooseColor(this.value);
          });
          nativePicker.addEventListener('change', function(e) {
            chooseColor(this.value);
            colorPop.classList.remove('is-open');
          });
        }

        document.addEventListener('click', function(e) {
          if (colorPop.classList.contains('is-open') && !colorPop.contains(e.target) && e.target !== colorBtn && !colorBtn.contains(e.target)) {
            colorPop.classList.remove('is-open');
          }
        });
      }

      // 点击示波器切换播放 (排除控件栏与色彩弹窗)
      wrap.addEventListener('click', function(e) {
        if (e.target.closest('#sleepScopeControls, .sleep-color-palette-pop')) {
          return;
        }
        e.preventDefault();
        sleepToggleMusic();
      });

      // 键盘无障碍支持
      wrap.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          sleepToggleMusic();
        }
      });

      // 页面可见性与Tab切换监听
      document.addEventListener('visibilitychange', function() {
        if (document.hidden) stopLoop();
        else if (isVisible()) startLoop();
      });

      window.addEventListener('resize', function() {
        if (isVisible() && !animId) startLoop();
      });

      startLoop();
    }

    return {
      init: init,
      start: startLoop,
      stop: stopLoop,
      setColor: chooseColor,
      getColor: function() { return userColor; }
    };
  })();
  window.sleepOscilloscope = sleepOscilloscope;

"""

new_content = prefix + CLEAN_SLEEP_OSCILLOSCOPE + suffix
with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
    f.write(new_content)

print("[SUCCESS] sleepOscilloscope cleanly replaced in _template.html")
