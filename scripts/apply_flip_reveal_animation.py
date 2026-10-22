# -*- coding: utf-8 -*-
"""
Add flip-reveal synchronized animation:
When the card is flipped, the awareness text card reveals with elegant staggered motion.
When unflipped, an inviting, aesthetic placeholder covers it.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_path = os.path.join(ROOT, "frontend", "_template.html")

with open(template_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update CSS around .awareness-word-card
old_word_card_css = """.awareness-word-card {
  background: linear-gradient(155deg, #FAF6EE 0%, #F5EFE3 100%);
  border: 1px solid #D9CEBD;
  border-radius: 16px;
  padding: 24px 22px 20px;
  box-shadow: 0 8px 24px rgba(35, 30, 25, 0.08);
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}"""

new_word_card_css = """.awareness-word-card {
  background: linear-gradient(155deg, #FAF6EE 0%, #F5EFE3 100%);
  border: 1px solid #D9CEBD;
  border-radius: 16px;
  box-shadow: 0 8px 28px rgba(35, 30, 25, 0.08);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 480px;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}

/* 1. 未翻开状态层 (沉静、神秘、吸引点击) */
.awareness-word-card-unrevealed {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(155deg, rgba(250, 246, 238, 0.98) 0%, rgba(245, 239, 227, 0.98) 100%);
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  z-index: 5;
  opacity: 1;
  transform: scale(1);
  transition: opacity 0.4s cubic-bezier(0.2, 0.8, 0.2, 1), transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1), visibility 0.4s;
  cursor: pointer;
}

.compass-mini-ring {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  border: 1.5px dashed #C9BEAD;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  animation: compassSpin 20s linear infinite;
  box-shadow: 0 0 16px rgba(196, 164, 124, 0.2);
}

.compass-mini-star {
  font-size: 20px;
  color: var(--color-gold);
  line-height: 1;
}

.unrevealed-title {
  font-family: var(--font-serif);
  font-size: 19px;
  font-weight: 700;
  color: var(--color-ink);
  letter-spacing: 0.06em;
  margin-bottom: 10px;
}

.unrevealed-desc {
  font-size: 13.5px;
  color: var(--color-muted);
  line-height: 1.7;
  margin: 0 0 20px;
  max-width: 250px;
}

.unrevealed-btn-hint {
  font-size: 12px;
  color: var(--color-primary);
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--color-gold-border);
  padding: 6px 16px;
  border-radius: 20px;
  letter-spacing: 0.04em;
  transition: all 0.2s ease;
}

.awareness-word-card-unrevealed:hover .unrevealed-btn-hint {
  background: var(--color-primary);
  color: #FAF6EF;
  border-color: var(--color-primary);
}

/* 翻开时未显现层淡出隐藏 */
.awareness-word-card.is-revealed .awareness-word-card-unrevealed {
  opacity: 0;
  transform: scale(0.95);
  visibility: hidden;
  pointer-events: none;
}

/* 2. 翻开后的内容卡片动效 */
.awareness-word-card-content {
  padding: 24px 22px 20px;
  display: flex;
  flex-direction: column;
  flex: 1;
  opacity: 0;
  transform: translateY(18px);
  filter: blur(6px);
  transition: opacity 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) 0.12s,
              transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) 0.12s,
              filter 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) 0.12s;
}

.awareness-word-card.is-revealed .awareness-word-card-content {
  opacity: 1;
  transform: translateY(0);
  filter: blur(0);
}

/* 标题、问句与交互错峰滑入动效 (Staggered Animation) */
.awareness-word-card.is-revealed .card-front-title {
  animation: cardFadeSlideIn 0.55s cubic-bezier(0.16, 1, 0.3, 1) 0.18s backwards;
}
.awareness-word-card.is-revealed .card-front-question {
  animation: cardFadeSlideIn 0.65s cubic-bezier(0.16, 1, 0.3, 1) 0.28s backwards;
}
.awareness-word-card.is-revealed .card-front-desc {
  animation: cardFadeSlideIn 0.65s cubic-bezier(0.16, 1, 0.3, 1) 0.38s backwards;
}
.awareness-word-card.is-revealed .awareness-controls-dock {
  animation: cardFadeSlideIn 0.65s cubic-bezier(0.16, 1, 0.3, 1) 0.44s backwards;
}

@keyframes cardFadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(16px);
    filter: blur(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

@keyframes compassSpin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}"""

assert old_word_card_css in text, "old_word_card_css not found!"
text = text.replace(old_word_card_css, new_word_card_css, 1)

# 2. Update HTML of .awareness-text-column
old_html_col = """          <!-- 右侧：文字卡片 (字卡 · 觉察反思与交互引导) -->
          <div class="awareness-text-column">
            <div class="awareness-word-card">
              <div class="awareness-word-card-badge">
                <span class="badge-label">01 觉察字卡 · 照见内心</span>
                <span class="tap-hint" style="font-size:11px;cursor:pointer;" onclick="var b=$('awarenessCardBox');if(b)b.click();">↺ 翻转图卡</span>
              </div>
              <div class="card-front-title" id="awFrontTitle">总想让所有人满意</div>
              <div class="card-front-question serif" id="awFrontQuestion">「我是不是很久没有认真问过自己，真正想要的是什么？」</div>
              <div class="card-front-desc" id="awFrontDesc">这是一张用于自我反思的提示卡，不代表对你的判断。</div>

              <!-- 觉察交互底栏 (嵌入右侧字卡底部) -->
              <div class="awareness-controls-dock" style="margin-top:auto;width:100%;max-width:none;">
                <div class="awareness-actions-grid">
                  <button class="btn sm" id="btnAwResonates">很像我</button>
                  <button class="btn sm ghost" id="btnAwPartly">有一点像</button>
                  <button class="btn sm secondary" id="btnAwChange">换一张 ↻</button>
                  <button class="btn sm secondary" id="btnAwCancel">先不继续</button>
                </div>
                <div class="awareness-followup-box hidden" id="awFollowupBox">
                  <div style="font-weight:600;margin-bottom:6px;color:var(--color-primary);" id="awFollowupTitle">深入一笔（选填）：</div>
                  <div id="awFollowupText" style="margin-bottom:8px;font-size:13px;">最近有没有一件事，你其实不愿意做，却因为担心别人失望而答应了？</div>
                  <input type="text" class="form-input" id="awFollowupInput" placeholder="写下一两句延伸感受…" style="font-size:13px;padding:6px 10px;">
                </div>
                <div style="margin-top:14px;width:100%;" id="awProceedWrap" class="hidden">
                  <button class="btn lg" id="btnAwProceed" style="width:100%;">带上这张牌，进入解忧流程 →</button>
                </div>
              </div>
            </div>
          </div>"""

new_html_col = """          <!-- 右侧：文字卡片 (字卡 · 觉察反思与交互引导) -->
          <div class="awareness-text-column">
            <div class="awareness-word-card" id="awarenessWordCard">
              <!-- 未翻开状态提示遮罩 (保持神秘感与期待感) -->
              <div class="awareness-word-card-unrevealed" id="awUnrevealedCover" onclick="var b=$('awarenessCardBox');if(b)b.click();" title="点击翻开卡牌">
                <div class="compass-mini-ring">
                  <div class="compass-mini-star">✦</div>
                </div>
                <div class="unrevealed-title">凝神静气 · 照见内心</div>
                <p class="unrevealed-desc">
                  万般心事，皆有来处。<br>轻触左侧卡牌，翻开今日心境照见。
                </p>
                <div class="unrevealed-btn-hint">
                  <span>点击翻开卡牌 ↺</span>
                </div>
              </div>

              <!-- 翻开后动态显现的觉察内容 -->
              <div class="awareness-word-card-content">
                <div class="awareness-word-card-badge">
                  <span class="badge-label">01 觉察字卡 · 照见内心</span>
                  <span class="tap-hint" style="font-size:11px;cursor:pointer;" onclick="var b=$('awarenessCardBox');if(b)b.click();">↺ 翻转图卡</span>
                </div>
                <div class="card-front-title" id="awFrontTitle">总想让所有人满意</div>
                <div class="card-front-question serif" id="awFrontQuestion">「我是不是很久没有认真问过自己，真正想要的是什么？」</div>
                <div class="card-front-desc" id="awFrontDesc">这是一张用于自我反思的提示卡，不代表对你的判断。</div>

                <!-- 觉察交互底栏 (嵌入右侧字卡底部) -->
                <div class="awareness-controls-dock" style="margin-top:auto;width:100%;max-width:none;">
                  <div class="awareness-actions-grid">
                    <button class="btn sm" id="btnAwResonates">很像我</button>
                    <button class="btn sm ghost" id="btnAwPartly">有一点像</button>
                    <button class="btn sm secondary" id="btnAwChange">换一张 ↻</button>
                    <button class="btn sm secondary" id="btnAwCancel">先不继续</button>
                  </div>
                  <div class="awareness-followup-box hidden" id="awFollowupBox">
                    <div style="font-weight:600;margin-bottom:6px;color:var(--color-primary);" id="awFollowupTitle">深入一笔（选填）：</div>
                    <div id="awFollowupText" style="margin-bottom:8px;font-size:13px;">最近有没有一件事，你其实不愿意做，却因为担心别人失望而答应了？</div>
                    <input type="text" class="form-input" id="awFollowupInput" placeholder="写下一两句延伸感受…" style="font-size:13px;padding:6px 10px;">
                  </div>
                  <div style="margin-top:14px;width:100%;" id="awProceedWrap" class="hidden">
                    <button class="btn lg" id="btnAwProceed" style="width:100%;">带上这张牌，进入解忧流程 →</button>
                  </div>
                </div>
              </div>
            </div>
          </div>"""

assert old_html_col in text, "old_html_col not found!"
text = text.replace(old_html_col, new_html_col, 1)

# 3. Update JS flip logic to synchronize wordCard .is-revealed
old_js_flip = """    var awarenessCardBox = $('awarenessCardBox');
    if (awarenessCardBox) {
      awarenessCardBox.onclick = function(e) {
        if (!appState.awarenessFlipped) {
          awarenessCardBox.classList.add('is-flipped');
          appState.awarenessFlipped = true;
        } else {
          awarenessCardBox.classList.remove('is-flipped');
          appState.awarenessFlipped = false;
        }
      };
    }"""

new_js_flip = """    function updateAwarenessFlipUI(isFlipped) {
      appState.awarenessFlipped = !!isFlipped;
      var box = $('awarenessCardBox');
      var wordCard = $('awarenessWordCard');
      if (box) {
        if (isFlipped) box.classList.add('is-flipped');
        else box.classList.remove('is-flipped');
      }
      if (wordCard) {
        if (isFlipped) wordCard.classList.add('is-revealed');
        else wordCard.classList.remove('is-revealed');
      }
    }

    var awarenessCardBox = $('awarenessCardBox');
    if (awarenessCardBox) {
      awarenessCardBox.onclick = function(e) {
        updateAwarenessFlipUI(!appState.awarenessFlipped);
      };
    }"""

assert old_js_flip in text, "old_js_flip not found!"
text = text.replace(old_js_flip, new_js_flip, 1)

# 4. Update btnAwChange to use updateAwarenessFlipUI
old_btn_change = """    $('btnAwChange').onclick = function(e) {
      e.stopPropagation();
      var box = $('awarenessCardBox');
      if (box) box.classList.remove('is-flipped');
      appState.awarenessFlipped = false;
      setTimeout(function() {
        var total = (CARDS_MINDSET && CARDS_MINDSET.length) ? CARDS_MINDSET.length : 16;
        var current = appState.awarenessIndex;
        var next = Math.floor(Math.random() * (total - 1));
        if (next >= current) next = (next + 1) % total;
        appState.awarenessIndex = next;
        renderAwarenessCard(appState.awarenessIndex);
        if (box) box.classList.add('is-flipped');
        appState.awarenessFlipped = true;
      }, 180);
    };"""

new_btn_change = """    $('btnAwChange').onclick = function(e) {
      e.stopPropagation();
      updateAwarenessFlipUI(false);
      setTimeout(function() {
        var total = (CARDS_MINDSET && CARDS_MINDSET.length) ? CARDS_MINDSET.length : 16;
        var current = appState.awarenessIndex;
        var next = Math.floor(Math.random() * (total - 1));
        if (next >= current) next = (next + 1) % total;
        appState.awarenessIndex = next;
        renderAwarenessCard(appState.awarenessIndex);
        updateAwarenessFlipUI(true);
      }, 240);
    };"""

assert old_btn_change in text, "old_btn_change not found!"
text = text.replace(old_btn_change, new_btn_change, 1)

# 5. In renderAwarenessCard, reset flip state
old_render_reset = """    var cardBox = $('awarenessCardBox');
    if (cardBox) {
      cardBox.classList.remove('is-flipped');"""

new_render_reset = """    var cardBox = $('awarenessCardBox');
    if (cardBox) {
      if (typeof updateAwarenessFlipUI === 'function') updateAwarenessFlipUI(false);
      else cardBox.classList.remove('is-flipped');"""

assert old_render_reset in text, "old_render_reset not found!"
text = text.replace(old_render_reset, new_render_reset, 1)

with open(template_path, "w", encoding="utf-8") as f:
    f.write(text)

print("[SUCCESS] Flip-reveal animation updated in _template.html!")
