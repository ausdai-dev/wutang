# -*- coding: utf-8 -*-
"""
悟堂 · 东方解忧处 —— 背景音乐集成补丁脚本
将两首禅意背景音（Flowing Mind、Zen Meditation）与播放控制组件（顶栏开关、曲目选择、音量调节、悬浮气泡）注入前端模板
"""
import os
import sys
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

BGM_CSS = """
/* ==========================================================================
   悟堂 · 禅意背景音乐播放器 (Zen Background Music Player)
   ========================================================================== */
.bgm-control-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}
.bgm-btn {
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #DFD8CC;
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 12.5px;
  color: #5C564E;
  cursor: pointer;
  transition: all var(--trans);
  backdrop-filter: blur(4px);
  display: inline-flex;
  align-items: center;
  gap: 7px;
  user-select: none;
}
.bgm-btn:hover {
  background: #FFFFFF;
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.bgm-btn.is-playing {
  background: #FFF9F7;
  border-color: var(--color-primary-border);
  color: var(--color-primary);
  box-shadow: 0 2px 10px rgba(142,41,39,0.1);
}
.bgm-icon-wave {
  display: inline-flex;
  align-items: flex-end;
  gap: 2px;
  height: 12px;
  width: 12px;
}
.bgm-icon-wave span {
  display: inline-block;
  width: 2px;
  background-color: currentColor;
  border-radius: 1px;
  height: 4px;
  transition: height 0.2s;
}
.bgm-btn.is-playing .bgm-icon-wave span:nth-child(1) {
  animation: bgmWave 1.1s ease-in-out infinite 0.1s;
}
.bgm-btn.is-playing .bgm-icon-wave span:nth-child(2) {
  animation: bgmWave 1.1s ease-in-out infinite 0.35s;
}
.bgm-btn.is-playing .bgm-icon-wave span:nth-child(3) {
  animation: bgmWave 1.1s ease-in-out infinite 0.2s;
}
@keyframes bgmWave {
  0%, 100% { height: 3px; }
  50% { height: 12px; }
}

/* 禅意音乐下拉卡片 */
.bgm-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 310px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  box-shadow: var(--shadow-lg);
  padding: 16px 18px;
  z-index: 1000;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-6px);
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  pointer-events: none;
}
.bgm-panel.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  pointer-events: auto;
}
.bgm-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed var(--color-border);
}
.bgm-panel-title {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--color-ink);
  display: flex;
  align-items: center;
  gap: 6px;
}
.bgm-track-list {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-bottom: 12px;
}
.bgm-track-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: var(--color-surface-card);
  cursor: pointer;
  transition: all var(--trans);
  font-size: 13px;
  user-select: none;
}
.bgm-track-item:hover {
  background: #F4EFE6;
  border-color: #E2D9CC;
}
.bgm-track-item.active {
  background: var(--color-primary-light);
  border-color: var(--color-primary-border);
  color: var(--color-primary);
  font-weight: 600;
}
.bgm-track-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}
.bgm-track-sub {
  font-size: 11px;
  color: var(--color-muted);
  font-weight: normal;
  margin-top: 2px;
}
.bgm-track-item.active .bgm-track-sub {
  color: #A04A47;
}
.bgm-controls-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 10px;
}
.bgm-ctrl-btn {
  background: #FAF8F4;
  border: 1px solid #DFD8CC;
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 12px;
  cursor: pointer;
  color: #5C564E;
  transition: all var(--trans);
  flex: 1;
  text-align: center;
}
.bgm-ctrl-btn:hover {
  background: #FFFFFF;
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.bgm-volume-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: var(--color-muted);
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #F0ECE4;
}
.bgm-volume-slider {
  flex: 1;
  -webkit-appearance: none;
  height: 4px;
  border-radius: 2px;
  background: #E5DFD5;
  outline: none;
}
.bgm-volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}

/* 屏幕右下角悬浮静心音乐气泡 */
.bgm-floating-pill {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 990;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #E2D9CC;
  box-shadow: var(--shadow-md);
  border-radius: 24px;
  padding: 8px 14px;
  font-size: 12.5px;
  color: var(--color-ink);
  cursor: pointer;
  backdrop-filter: blur(8px);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  user-select: none;
}
.bgm-floating-pill:hover {
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary-border);
  transform: translateY(-2px);
}
.bgm-floating-pill.is-playing {
  border-color: var(--color-primary-border);
  background: rgba(255, 250, 248, 0.96);
  color: var(--color-primary);
}
.bgm-disc {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #782120, #962E2D);
  color: #FAF5EE;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  flex-shrink: 0;
}
.bgm-floating-pill.is-playing .bgm-disc {
  animation: bgmSpin 4s linear infinite;
}
@keyframes bgmSpin {
  100% { transform: rotate(360deg); }
}
@media (max-width: 600px) {
  .bgm-panel {
    right: -20px;
    width: 270px;
  }
  .bgm-floating-pill {
    bottom: 16px;
    right: 16px;
    padding: 7px 12px;
    font-size: 11.5px;
  }
}
"""

BGM_HEADER_HTML = """
      <!-- 悟堂 · 禅意背景音乐开关与面板 (PRD 东方静心音疗) -->
      <div class="bgm-control-wrap" id="bgmControlWrap">
        <button class="bgm-btn" id="btnBgmToggle" title="悟堂禅意背景音乐（点击播放/暂停，点击右侧箭头展开曲目与音量）" aria-label="背景音乐">
          <span class="bgm-icon-wave">
            <span></span><span></span><span></span>
          </span>
          <span id="bgmStatusText">静心音乐: 关</span>
          <span class="bgm-menu-arrow" id="btnBgmMenuArrow" title="曲目与音量设置" style="font-size:10px;opacity:0.6;margin-left:3px;cursor:pointer;">▾</span>
        </button>

        <!-- 悬浮曲目与音量面板 -->
        <div class="bgm-panel" id="bgmPanel">
          <div class="bgm-panel-header">
            <span class="bgm-panel-title">🌿 悟堂 · 禅意背景音</span>
            <span id="bgmClosePanel" style="cursor:pointer;color:var(--color-muted);font-size:16px;line-height:1;" title="收起面板">×</span>
          </div>

          <div class="bgm-track-list" id="bgmTrackList">
            <!-- 动态渲染曲目 -->
          </div>

          <div class="bgm-controls-row">
            <button class="bgm-ctrl-btn" id="btnBgmPrev" title="上一曲">⏮ 上一曲</button>
            <button class="bgm-ctrl-btn" id="btnBgmPlayPause" style="color:var(--color-primary);font-weight:600;">▶ 播放</button>
            <button class="bgm-ctrl-btn" id="btnBgmNext" title="下一曲">下一曲 ⏭</button>
          </div>

          <div class="bgm-volume-row">
            <span id="bgmVolIcon" style="cursor:pointer;user-select:none;" title="静音切换">🔉</span>
            <input type="range" id="bgmVolumeSlider" class="bgm-volume-slider" min="0" max="100" value="35" title="音量调节">
            <span id="bgmVolVal" style="min-width:32px;text-align:right;">35%</span>
          </div>
        </div>
      </div>
"""

BGM_BODY_HTML = """
<!-- 悟堂 · 禅意背景音乐音频与屏幕右下角悬浮切换气泡 -->
<audio id="bgmAudio" preload="auto"></audio>
<div class="bgm-floating-pill" id="bgmFloatingPill" title="点击开关背景音乐，右侧顶栏可选择曲目与音量">
  <div class="bgm-disc">♫</div>
  <span id="bgmFloatingText">静心音乐: 关</span>
</div>
"""

BGM_JS = """
  // ==========================================================================
  // 悟堂 · 禅意背景音乐控制引擎 (Zen Ambient Background Music Engine)
  // 包含《Flowing Mind 行云流水》与《Zen Meditation 禅境冥想》两首东方禅意音轨
  // ==========================================================================
  var bgmEngine = (function() {
    var TRACKS = [
      {
        id: 'flowing_mind',
        name: '行云流水',
        subtitle: 'Flowing Mind',
        src: 'assets/audio/flowing_mind.m4a',
        fallbackSrc: 'assets/audio/Flowing Mind.m4a',
        desc: '空灵澄澈 · 清心释压'
      },
      {
        id: 'zen_meditation',
        name: '禅境冥想',
        subtitle: 'Zen Meditation',
        src: 'assets/audio/zen_meditation.m4a',
        fallbackSrc: 'assets/audio/Zen Meditation.m4a',
        desc: '沉静幽远 · 凝神入定'
      }
    ];

    var currentIndex = 0;
    var isPlaying = false;
    var volume = 0.35; // 默认 35% 舒适背景音量
    var audio = null;
    var isPanelOpen = false;

    function init() {
      audio = $('bgmAudio');
      if (!audio) {
        audio = new Audio();
        audio.id = 'bgmAudio';
        audio.preload = 'auto';
        document.body.appendChild(audio);
      }

      // 读取本地持久化偏好
      try {
        var saved = localStorage.getItem('wutang_bgm_pref');
        if (saved) {
          var pref = JSON.parse(saved);
          if (typeof pref.volume === 'number') volume = Math.max(0, Math.min(1, pref.volume));
          if (typeof pref.currentIndex === 'number' && pref.currentIndex >= 0 && pref.currentIndex < TRACKS.length) {
            currentIndex = pref.currentIndex;
          }
        }
      } catch (e) {}

      audio.volume = volume;
      loadTrack(currentIndex, false);

      // 事件监听
      audio.addEventListener('ended', function() {
        nextTrack(true);
      });

      audio.addEventListener('play', function() {
        isPlaying = true;
        updateUI();
      });

      audio.addEventListener('pause', function() {
        isPlaying = false;
        updateUI();
      });

      audio.addEventListener('error', function() {
        var track = TRACKS[currentIndex];
        if (track && track.fallbackSrc && audio.src !== track.fallbackSrc) {
          audio.src = track.fallbackSrc;
          if (isPlaying) {
            audio.play().catch(function() {});
          }
        }
      });

      renderTrackList();
      updateUI();
      setupBgmEvents();
    }

    function savePref() {
      try {
        localStorage.setItem('wutang_bgm_pref', JSON.stringify({
          volume: volume,
          currentIndex: currentIndex
        }));
      } catch (e) {}
    }

    function loadTrack(index, autoPlay) {
      if (index < 0 || index >= TRACKS.length) index = 0;
      currentIndex = index;
      var track = TRACKS[currentIndex];
      audio.src = track.src;
      savePref();
      renderTrackList();
      updateUI();

      if (autoPlay) {
        play();
      }
    }

    function play() {
      if (!audio.src) {
        audio.src = TRACKS[currentIndex].src;
      }
      var promise = audio.play();
      if (promise !== undefined) {
        promise.then(function() {
          isPlaying = true;
          updateUI();
        }).catch(function(err) {
          console.warn('[BGM] 浏览器自动播放拦截或音频加载未完成:', err);
          isPlaying = false;
          updateUI();
          if (typeof showToast === 'function') {
            showToast('请轻触屏幕以开启背景音乐');
          }
        });
      }
    }

    function pause() {
      audio.pause();
      isPlaying = false;
      updateUI();
    }

    function togglePlay() {
      if (isPlaying) {
        pause();
      } else {
        play();
      }
    }

    function nextTrack(autoPlay) {
      var nextIdx = (currentIndex + 1) % TRACKS.length;
      loadTrack(nextIdx, autoPlay !== false);
    }

    function prevTrack(autoPlay) {
      var prevIdx = (currentIndex - 1 + TRACKS.length) % TRACKS.length;
      loadTrack(prevIdx, autoPlay !== false);
    }

    function setVolume(val) {
      volume = Math.max(0, Math.min(1, val));
      if (audio) audio.volume = volume;
      savePref();
      updateUI();
    }

    function renderTrackList() {
      var listEl = $('bgmTrackList');
      if (!listEl) return;
      var html = '';
      TRACKS.forEach(function(t, idx) {
        var isActive = (idx === currentIndex);
        html += '<div class="bgm-track-item ' + (isActive ? 'active' : '') + '" data-index="' + idx + '">'
          + '  <div class="bgm-track-info">'
          + '    <div style="display:flex;align-items:center;gap:6px;">'
          + '      <span style="font-size:12px;">' + (isActive && isPlaying ? '🔊' : (isActive ? '🎵' : '⚪')) + '</span>'
          + '      <strong style="font-size:13px;">' + esc(t.name) + '</strong>'
          + '      <span style="font-size:11px;color:var(--color-muted);">' + esc(t.subtitle) + '</span>'
          + '    </div>'
          + '    <span class="bgm-track-sub">' + esc(t.desc) + '</span>'
          + '  </div>'
          + '  <div style="font-size:11px;color:' + (isActive ? 'var(--color-primary)' : 'var(--color-muted)') + ';">'
          + (isActive && isPlaying ? '播放中' : (isActive ? '已选' : '播放'))
          + '  </div>'
          + '</div>';
      });
      listEl.innerHTML = html;

      // 绑定曲目点击
      var items = listEl.querySelectorAll('.bgm-track-item');
      items.forEach(function(item) {
        item.addEventListener('click', function(e) {
          e.stopPropagation();
          var idx = parseInt(item.getAttribute('data-index'), 10);
          if (idx === currentIndex && isPlaying) {
            pause();
          } else {
            loadTrack(idx, true);
          }
        });
      });
    }

    function updateUI() {
      var curTrack = TRACKS[currentIndex] || TRACKS[0];
      var toggleBtn = $('btnBgmToggle');
      var statusText = $('bgmStatusText');
      var playPauseBtn = $('btnBgmPlayPause');
      var floatingPill = $('bgmFloatingPill');
      var floatingText = $('bgmFloatingText');
      var volSlider = $('bgmVolumeSlider');
      var volVal = $('bgmVolVal');
      var volIcon = $('bgmVolIcon');

      if (toggleBtn) {
        if (isPlaying) {
          toggleBtn.classList.add('is-playing');
          toggleBtn.title = '背景音乐播放中: ' + curTrack.name + ' (' + curTrack.subtitle + ') · 点击暂停';
        } else {
          toggleBtn.classList.remove('is-playing');
          toggleBtn.title = '背景音乐已暂停 · 点击播放 ' + curTrack.name;
        }
      }

      if (statusText) {
        statusText.textContent = isPlaying ? ('正在播放: ' + curTrack.name) : '静心音乐: 关';
      }

      if (playPauseBtn) {
        playPauseBtn.textContent = isPlaying ? '⏸ 暂停' : '▶ 播放';
      }

      if (floatingPill) {
        if (isPlaying) {
          floatingPill.classList.add('is-playing');
          floatingPill.title = '当前播放: ' + curTrack.name + ' · 点击暂停，双击设置';
        } else {
          floatingPill.classList.remove('is-playing');
          floatingPill.title = '静心音乐已暂停 · 点击播放 ' + curTrack.name;
        }
      }

      if (floatingText) {
        floatingText.textContent = isPlaying ? ('♫ ' + curTrack.name) : '静心音乐: 关';
      }

      if (volSlider) {
        var pct = Math.round(volume * 100);
        volSlider.value = pct;
        if (volVal) volVal.textContent = pct + '%';
        if (volIcon) {
          volIcon.textContent = volume === 0 ? '🔇' : (volume < 0.5 ? '🔉' : '🔊');
        }
      }
    }

    function togglePanel(e) {
      if (e) e.stopPropagation();
      var panel = $('bgmPanel');
      if (!panel) return;
      isPanelOpen = !isPanelOpen;
      if (isPanelOpen) {
        panel.classList.add('show');
        renderTrackList();
      } else {
        panel.classList.remove('show');
      }
    }

    function closePanel() {
      var panel = $('bgmPanel');
      if (panel) {
        panel.classList.remove('show');
        isPanelOpen = false;
      }
    }

    function setupBgmEvents() {
      var btnToggle = $('btnBgmToggle');
      var btnMenuArrow = $('btnBgmMenuArrow');
      var btnPlayPause = $('btnBgmPlayPause');
      var btnPrev = $('btnBgmPrev');
      var btnNext = $('btnBgmNext');
      var btnClose = $('bgmClosePanel');
      var volSlider = $('bgmVolumeSlider');
      var volIcon = $('bgmVolIcon');
      var floatingPill = $('bgmFloatingPill');
      var panel = $('bgmPanel');

      // 点击主按钮主体：开关播放/暂停
      if (btnToggle) {
        btnToggle.addEventListener('click', function(e) {
          if (e.target && e.target.id === 'btnBgmMenuArrow') {
            togglePanel(e);
            return;
          }
          togglePlay();
        });
      }

      if (btnMenuArrow) {
        btnMenuArrow.addEventListener('click', function(e) {
          togglePanel(e);
        });
      }

      if (floatingPill) {
        floatingPill.addEventListener('click', function() {
          togglePlay();
        });
      }

      if (btnPlayPause) {
        btnPlayPause.addEventListener('click', function(e) {
          e.stopPropagation();
          togglePlay();
        });
      }

      if (btnPrev) {
        btnPrev.addEventListener('click', function(e) {
          e.stopPropagation();
          prevTrack(true);
        });
      }

      if (btnNext) {
        btnNext.addEventListener('click', function(e) {
          e.stopPropagation();
          nextTrack(true);
        });
      }

      if (btnClose) {
        btnClose.addEventListener('click', function(e) {
          e.stopPropagation();
          closePanel();
        });
      }

      if (volSlider) {
        volSlider.addEventListener('input', function(e) {
          e.stopPropagation();
          var val = parseFloat(volSlider.value) / 100;
          setVolume(val);
        });
      }

      if (volIcon) {
        volIcon.addEventListener('click', function(e) {
          e.stopPropagation();
          if (volume > 0) {
            volIcon.setAttribute('data-last-vol', volume);
            setVolume(0);
          } else {
            var last = parseFloat(volIcon.getAttribute('data-last-vol') || '0.35');
            setVolume(last || 0.35);
          }
        });
      }

      // 点击外部自动收起面板
      document.addEventListener('click', function(e) {
        if (!panel || !isPanelOpen) return;
        var wrap = $('bgmControlWrap');
        if (wrap && !wrap.contains(e.target)) {
          closePanel();
        }
      });

      // 阻止面板内部点击冒泡
      if (panel) {
        panel.addEventListener('click', function(e) {
          e.stopPropagation();
        });
      }
    }

    return {
      init: init,
      play: play,
      pause: pause,
      togglePlay: togglePlay,
      nextTrack: nextTrack,
      prevTrack: prevTrack,
      setVolume: setVolume,
      togglePanel: togglePanel,
      closePanel: closePanel
    };
  })();
"""

def patch_template():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 注入 CSS (在 .header-action-btn:hover 规则后)
    if ".bgm-control-wrap" not in content:
        css_anchor = ".header-action-btn:hover {"
        idx = content.find(css_anchor)
        if idx != -1:
            # 找到闭合大括号
            close_idx = content.find("}", idx)
            if close_idx != -1:
                content = content[:close_idx+1] + "\n" + BGM_CSS + content[close_idx+1:]
                print("[✓] 成功注入 BGM CSS 样式")
        else:
            print("[!] 未找到 CSS 锚点")
    else:
        print("[-] BGM CSS 已存在")

    # 2. 注入顶栏开关与面板 (在 btnAiStatus 之后)
    if "btnBgmToggle" not in content:
        header_anchor = 'id="btnAiStatus"'
        idx = content.find(header_anchor)
        if idx != -1:
            close_btn = content.find("</button>", idx)
            if close_btn != -1:
                insert_pos = close_btn + len("</button>")
                content = content[:insert_pos] + "\n" + BGM_HEADER_HTML + content[insert_pos:]
                print("[✓] 成功注入顶栏 BGM 控制胶囊与面板")
        else:
            print("[!] 未找到顶栏按钮锚点")
    else:
        print("[-] 顶栏 BGM 控制按钮已存在")

    # 3. 注入 audio 标签与屏幕右下角悬浮切换气泡
    if "bgmAudio" not in content:
        toast_anchor = 'id="globalToast"'
        idx = content.find(toast_anchor)
        if idx != -1:
            close_div = content.find("</div>", idx)
            if close_div != -1:
                insert_pos = close_div + len("</div>")
                content = content[:insert_pos] + "\n" + BGM_BODY_HTML + content[insert_pos:]
                print("[✓] 成功注入 audio 标签与悬浮音乐气泡")
        else:
            print("[!] 未找到 globalToast 锚点")
    else:
        print("[-] audio 标签已存在")

    # 4. 注入 bgmEngine JavaScript 引擎
    if "var bgmEngine = " not in content:
        boot_anchor = "// 启动初始化"
        idx = content.find(boot_anchor)
        if idx != -1:
            content = content[:idx] + BGM_JS + "\n" + content[idx:]
            print("[✓] 成功注入 bgmEngine JS 引擎逻辑")
        else:
            print("[!] 未找到启动初始化锚点")
    else:
        print("[-] bgmEngine JS 已存在")

    # 5. 在 bootstrap() 中初始化 bgmEngine
    if "bgmEngine.init();" not in content:
        ai_anchor = "checkAiBackendStatus();"
        idx = content.find(ai_anchor)
        if idx != -1:
            insert_pos = idx + len(ai_anchor)
            content = content[:insert_pos] + "\n    bgmEngine.init();" + content[insert_pos:]
            print("[✓] 成功在 bootstrap() 中调用 bgmEngine.init()")
        else:
            print("[!] 未找到 checkAiBackendStatus 锚点")
    else:
        print("[-] bgmEngine.init() 调用已存在")

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("[✓] 模板文件写入完毕")

if __name__ == "__main__":
    patch_template()
