# -*- coding: utf-8 -*-
import os

with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Desktop CSS patch
target_css_1 = """.zen-card-stage-3d {
  perspective: 1200px;
  -webkit-perspective: 1200px;
  width: 340px;
  max-width: 86vw;
  aspect-ratio: 2 / 3;
  margin: 0 auto 16px;
  cursor: pointer;
}"""

replace_css_1 = """.zen-card-stage-3d {
  perspective: 1200px;
  -webkit-perspective: 1200px;
  width: 330px;
  max-width: 86vw;
  aspect-ratio: 2 / 3;
  margin: 0 auto 14px;
  cursor: pointer;
  position: relative;
}

/* 东方觉察牌 3D 翻转反面：宋代宣纸自省解忧笺 */
.zen-modal-back-face {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  transform: rotateY(180deg) translateZ(1px);
  -webkit-transform: rotateY(180deg) translateZ(1px);
  background: linear-gradient(180deg, #FDFBF7 0%, #F5EFE3 100%);
  border-radius: 12px;
  border: 2px solid #C4A47C;
  box-sizing: border-box;
  overflow: hidden;
  contain: paint;
  clip-path: inset(0 round 12px);
  -webkit-clip-path: inset(0 round 12px);
}

/* 反面独立柔和滚动画卷：彻底杜绝长文本溢出或遮盖底部按钮 */
.zen-modal-back-scroll {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 18px 16px 14px;
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-color: rgba(196, 164, 124, 0.45) transparent;
}
.zen-modal-back-scroll::-webkit-scrollbar {
  width: 4px;
}
.zen-modal-back-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.zen-modal-back-scroll::-webkit-scrollbar-thumb {
  background: rgba(196, 164, 124, 0.45);
  border-radius: 4px;
}

.zen-back-num-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.zen-modal-back-face h4 {
  font-family: var(--font-serif);
  margin: 0 0 6px;
  font-size: 20px;
  color: var(--color-ink);
  letter-spacing: 2px;
  line-height: 1.25;
}
.zen-back-gold-line {
  width: 36px;
  height: 2px;
  background: #B89658;
  margin-bottom: 8px;
  border-radius: 2px;
}
.zen-back-scene-label {
  font-size: 11px;
  font-weight: 600;
  color: #7A736C;
  margin-bottom: 4px;
  letter-spacing: 0.5px;
}
.zen-modal-back-face #zen96ModalBackScene {
  font-size: 12.5px;
  color: #4A443E;
  line-height: 1.6;
  margin: 0 0 8px;
  text-align: justify;
}
.zen-modal-back-face #zen96ModalBackQuestion {
  background: #F2ECE1;
  border-left: 3.5px solid #8E2927;
  padding: 8px 10px;
  border-radius: 5px;
  font-size: 12px;
  line-height: 1.55;
  color: #2C2825;
  margin-bottom: 8px;
}
.zen-back-flip-hint {
  font-size: 10.5px;
  color: #8E867E;
  text-align: center;
  padding: 2px 0 0;
  user-select: none;
}"""

# 2. Mobile Media Query CSS patch
target_css_2 = """  /* 3D 卡牌舞台：宽度按视口缩小自适应，2:3 黄金比例完美缩放居中，杜绝滚动条 */
  .zen-card-stage-3d {
    width: min(220px, 60vw) !important;
    max-width: 60vw !important;
    max-height: 48vh !important;
    aspect-ratio: 2 / 3 !important;
    height: auto !important;
    margin: 0 auto 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  #zen96ModalFlipper {
    width: 100% !important;
    height: 100% !important;
  }
  /* 反面文字卡在移动端缩放下的优雅保护 */
  .zen-modal-back-face {
    padding: 14px 12px !important;
  }
  .zen-modal-back-face h4 {
    font-size: 18px !important;
    margin: 0 0 6px !important;
  }
  .zen-modal-back-face p {
    font-size: 11.5px !important;
    line-height: 1.5 !important;
    margin: 0 0 6px !important;
  }
  .zen-modal-back-face #zen96ModalBackQuestion {
    font-size: 12px !important;
    line-height: 1.5 !important;
    padding: 8px 10px !important;
    margin-bottom: 8px !important;
  }
  #btnZen96JournalAction,
  #btnZen96FavToggle {
    font-size: 12px !important;
    padding: 6px 12px !important;
  }"""

replace_css_2 = """  /* 3D 卡牌舞台：宽度舒展自适应，2:3 黄金比例，自适应屏幕 */
  .zen-card-stage-3d {
    width: min(280px, 72vw) !important;
    max-width: 72vw !important;
    max-height: 52vh !important;
    aspect-ratio: 2 / 3 !important;
    height: auto !important;
    margin: 0 auto 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  #zen96ModalFlipper {
    width: 100% !important;
    height: 100% !important;
  }
  /* 移动端反面文字紧凑优雅微调 */
  .zen-modal-back-scroll {
    padding: 12px 12px 10px !important;
  }
  .zen-modal-back-face h4 {
    font-size: 17px !important;
    margin: 0 0 4px !important;
  }
  .zen-back-gold-line {
    margin-bottom: 6px !important;
  }
  .zen-back-scene-label {
    font-size: 10.5px !important;
    margin-bottom: 3px !important;
  }
  .zen-modal-back-face #zen96ModalBackScene {
    font-size: 11.5px !important;
    line-height: 1.5 !important;
    margin: 0 0 6px !important;
  }
  .zen-modal-back-face #zen96ModalBackQuestion {
    font-size: 11px !important;
    line-height: 1.45 !important;
    padding: 6px 8px !important;
    margin-bottom: 6px !important;
  }
  .zen-back-flip-hint {
    font-size: 9.5px !important;
  }
  #btnZen96JournalAction,
  #btnZen96FavToggle {
    font-size: 12px !important;
    padding: 6px 12px !important;
  }"""

# 3. HTML structure patch
target_html = """          <!-- 反面：宋代宣纸解忧自省笺 -->
          <div class="zen-modal-back-face" style="position:absolute;width:100%;height:100%;-webkit-backface-visibility:hidden;backface-visibility:hidden;transform:rotateY(180deg) translateZ(1px);-webkit-transform:rotateY(180deg) translateZ(1px);background:linear-gradient(180deg, #FDFBF7 0%, #F5EFE3 100%);border-radius:12px;border:2px solid #C4A47C;padding:24px 20px;display:flex;flex-direction:column;justify-content:space-between;text-align:left;box-sizing:border-box;overflow:hidden;">
            <div>
              <div class="zen-back-num-row" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-size:12px;color:#8E2927;font-weight:700;letter-spacing:1px;" id="zen96ModalBackNum">【因缘相惜 · 编号 13】</span>
                <span class="zen-back-tag" style="font-size:11px;color:#998A78;border:1px solid #D9CEBD;padding:1px 6px;border-radius:8px;">宋画心象</span>
              </div>
              <h4 style="font-family:var(--font-serif);margin:0 0 8px;font-size:22px;color:var(--color-ink);letter-spacing:2px;" id="zen96ModalBackTitle">【 无 常 】</h4>
              <div class="zen-back-gold-line" style="width:40px;height:2px;background:#B89658;margin-bottom:12px;border-radius:2px;"></div>
              <div>
                <div class="zen-back-scene-label" style="font-size:11.5px;font-weight:600;color:#7A736C;margin-bottom:4px;">【画面意境】</div>
                <p style="font-size:13px;color:#4A443E;line-height:1.7;margin:0 0 10px;" id="zen96ModalBackScene">一树桃花临水而开，石桌之上清茶半盏。春意盎然中花瓣随风轻落，水面微澜映照晴空。</p>
              </div>
            </div>

            <div>
              <div style="background:#F2ECE1;border-left:3.5px solid #8E2927;padding:10px 12px;border-radius:5px;font-size:13px;line-height:1.65;color:#2C2825;margin-bottom:10px;" id="zen96ModalBackQuestion">最近有什么变化让你难受？它是否也带来了新的可能？</div>
              <div class="zen-back-flip-hint" style="font-size:11px;color:#8E867E;text-align:center;">轻触任意处可翻回正面画卷</div>
            </div>
          </div>"""

replace_html = """          <!-- 反面：宋代宣纸解忧自省笺 -->
          <div class="zen-modal-back-face">
            <div class="zen-modal-back-scroll">
              <div>
                <div class="zen-back-num-row">
                  <span style="font-size:12px;color:#8E2927;font-weight:700;letter-spacing:1px;" id="zen96ModalBackNum">【因缘相惜 · 编号 13】</span>
                  <span class="zen-back-tag" style="font-size:11px;color:#998A78;border:1px solid #D9CEBD;padding:1px 6px;border-radius:8px;">宋画心象</span>
                </div>
                <h4 id="zen96ModalBackTitle">【 无 常 】</h4>
                <div class="zen-back-gold-line"></div>
                <div>
                  <div class="zen-back-scene-label">【画面意境】</div>
                  <p id="zen96ModalBackScene">一树桃花临水而开，石桌之上清茶半盏。春意盎然中花瓣随风轻落，水面微澜映照晴空。</p>
                </div>
              </div>

              <div>
                <div id="zen96ModalBackQuestion">最近有什么变化让你难受？它是否也带来了新的可能？</div>
                <div class="zen-back-flip-hint">轻触任意处可翻回正面画卷</div>
              </div>
            </div>
          </div>"""

# 4. Spacing for bottom buttons
target_btn_wrap = """      <!-- 底部操作与联动 -->
      <div style="display:flex;flex-direction:column;gap:10px;margin-top:4px;">"""

replace_btn_wrap = """      <!-- 底部操作与联动 -->
      <div style="display:flex;flex-direction:column;gap:10px;margin-top:14px;position:relative;z-index:5;">"""

# 5. JS flip touch guard patch
target_js = """  window.toggleZen96ModalFlip = function() {

    var flipper = $('zen96ModalFlipper');

    if (!flipper) return;

    var isFlipped = (flipper.style.transform === 'rotateY(180deg)');

    flipper.style.transform = isFlipped ? 'rotateY(0deg)' : 'rotateY(180deg)';

  };"""

replace_js = """  window._zenModalScrollActive = false;
  window.toggleZen96ModalFlip = function() {
    if (window._zenModalScrollActive) {
      window._zenModalScrollActive = false;
      return;
    }
    var flipper = $('zen96ModalFlipper');
    if (!flipper) return;
    var isFlipped = (flipper.style.transform === 'rotateY(180deg)');
    flipper.style.transform = isFlipped ? 'rotateY(0deg)' : 'rotateY(180deg)';
  };

  (function initZenCardFlipTouchGuard() {
    var stage = document.querySelector('.zen-card-stage-3d');
    if (!stage) return;
    var touchStartY = 0;
    stage.addEventListener('touchstart', function(e) {
      if (e.touches && e.touches[0]) {
        touchStartY = e.touches[0].clientY;
      }
    }, { passive: true });
    stage.addEventListener('touchmove', function(e) {
      if (e.touches && e.touches[0]) {
        if (Math.abs(e.touches[0].clientY - touchStartY) > 8) {
          window._zenModalScrollActive = true;
        }
      }
    }, { passive: true });
    stage.addEventListener('touchend', function() {
      setTimeout(function() {
        window._zenModalScrollActive = false;
      }, 150);
    }, { passive: true });
  })();"""

# Normalize CRLF / LF for robust matching
def normalize(s):
    return s.replace('\r\n', '\n')

content_norm = normalize(content)
target_css_1_norm = normalize(target_css_1)
replace_css_1_norm = normalize(replace_css_1)
target_css_2_norm = normalize(target_css_2)
replace_css_2_norm = normalize(replace_css_2)
target_html_norm = normalize(target_html)
replace_html_norm = normalize(replace_html)
target_btn_wrap_norm = normalize(target_btn_wrap)
replace_btn_wrap_norm = normalize(replace_btn_wrap)
target_js_norm = normalize(target_js)
replace_js_norm = normalize(replace_js)

assert target_css_1_norm in content_norm, "target_css_1 not found"
content_norm = content_norm.replace(target_css_1_norm, replace_css_1_norm, 1)

assert target_css_2_norm in content_norm, "target_css_2 not found"
content_norm = content_norm.replace(target_css_2_norm, replace_css_2_norm, 1)

assert target_html_norm in content_norm, "target_html not found"
content_norm = content_norm.replace(target_html_norm, replace_html_norm, 1)

assert target_btn_wrap_norm in content_norm, "target_btn_wrap not found"
content_norm = content_norm.replace(target_btn_wrap_norm, replace_btn_wrap_norm, 1)

assert target_js_norm in content_norm, "target_js not found"
content_norm = content_norm.replace(target_js_norm, replace_js_norm, 1)

with open('frontend/_template.html', 'w', encoding='utf-8') as f:
    f.write(content_norm)

print("[OK] frontend/_template.html successfully patched!")
