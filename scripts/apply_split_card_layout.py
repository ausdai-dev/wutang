# -*- coding: utf-8 -*-
"""
Update frontend/_template.html:
Move text card to the right side of the card image (split layout).
Card image on the left has 0 text overlay, showing the pure watercolor artwork.
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_path = os.path.join(ROOT, "frontend", "_template.html")

with open(template_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update CSS
old_stage_css = """.awareness-stage {
  perspective: 1200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 18px 0 24px;
  width: 100%;
}
.awareness-card-container {
  width: 320px;
  height: 480px;
  aspect-ratio: 2 / 3;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);
  cursor: pointer;
  margin: 0 auto;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(34, 31, 27, 0.12);
}"""

new_stage_css = """.awareness-stage {
  perspective: 1200px;
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: stretch;
  gap: 28px;
  margin: 18px auto 24px;
  width: 100%;
  max-width: 800px;
  box-sizing: border-box;
}
.awareness-card-column {
  flex: 0 0 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.awareness-card-container {
  width: 320px;
  height: 480px;
  aspect-ratio: 2 / 3;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);
  cursor: pointer;
  margin: 0 auto;
  border-radius: 16px;
  box-shadow: 0 12px 32px rgba(34, 31, 27, 0.15);
}
.awareness-text-column {
  flex: 1 1 360px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  min-width: 300px;
}
.awareness-word-card {
  background: linear-gradient(155deg, #FAF6EE 0%, #F5EFE3 100%);
  border: 1px solid #D9CEBD;
  border-radius: 16px;
  padding: 24px 22px 20px;
  box-shadow: 0 8px 24px rgba(35, 30, 25, 0.08);
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}
.awareness-word-card-badge {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px dashed rgba(201, 190, 173, 0.7);
}
.awareness-word-card-badge .badge-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 0.05em;
}
.awareness-word-card .card-front-title {
  font-family: var(--font-serif);
  font-size: 20px;
  font-weight: 700;
  color: var(--color-ink);
  letter-spacing: 0.06em;
  margin: 0 0 14px;
  text-align: left;
}
.awareness-word-card .card-front-question {
  font-family: var(--font-serif);
  font-size: 17.5px;
  font-weight: 600;
  color: var(--color-ink);
  line-height: 1.68;
  letter-spacing: 0.02em;
  margin: 0 0 16px;
  text-align: left;
  padding: 0;
}
.awareness-word-card .card-front-desc {
  font-size: 13px;
  color: #726A5E;
  line-height: 1.6;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(210, 199, 182, 0.5);
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 16px;
  text-align: left;
  max-width: 100%;
}
@media (max-width: 680px) {
  .awareness-stage {
    flex-direction: column;
    align-items: center;
    gap: 20px;
  }
  .awareness-card-column {
    flex: 0 0 auto;
  }
  .awareness-text-column {
    width: 100%;
    max-width: 360px;
  }
}"""

assert old_stage_css in text, "old_stage_css not found!"
text = text.replace(old_stage_css, new_stage_css, 1)

# 2. Update .awareness-card-front CSS to be 100% clean, no text
old_front_css = """.awareness-card-front {
  background: #FAF7F2;
  transform: rotateY(180deg);
  text-align: center;
  padding: 24px 18px 20px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  box-sizing: border-box;
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.08);
}"""

new_front_css = """.awareness-card-front {
  background: #FAF7F2;
  transform: rotateY(180deg);
  text-align: center;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  box-sizing: border-box;
  background-size: cover;
  background-position: center;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.05);
}
.card-front-flip-tip {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.95);
  background: rgba(35, 30, 25, 0.45);
  padding: 4px 10px;
  border-radius: 12px;
  backdrop-filter: blur(4px);
  margin: 0 auto 6px;
  letter-spacing: 0.04em;
  user-select: none;
}"""

assert old_front_css in text, "old_front_css not found!"
text = text.replace(old_front_css, new_front_css, 1)

# 3. Update HTML structure of entryCardArea
old_html_block = """        <div class="awareness-stage">
          <div class="awareness-card-container" id="awarenessCardBox" title="点击翻转卡牌">
            <!-- 卡背 (3D 动态金色天体罗盘) -->
            <div class="awareness-card-face awareness-card-back card-3d-back">
              <div class="card-corner tl"></div>
              <div class="card-corner tr"></div>
              <div class="card-corner bl"></div>
              <div class="card-corner br"></div>
              <div class="card-back-header">SUBCONSCIOUS</div>
              <div class="card-back-center" style="height:170px;">
                <div class="card-orbit-ring" style="width:140px;height:140px;"></div>
                <div class="card-orbit-ring-inner" style="width:105px;height:105px;"></div>
                <div class="card-starburst">
                  <div class="card-starburst-ray v" style="height:64px;"></div>
                  <div class="card-starburst-ray h" style="width:64px;"></div>
                  <div class="card-starburst-ray d1" style="height:48px;"></div>
                  <div class="card-starburst-ray d2" style="height:48px;"></div>
                  <div class="card-core-gem" style="width:34px;height:34px;font-size:16px;">悟</div>
                </div>
              </div>
              <div class="card-back-footer">
                <span style="font-size:14px;font-weight:600;color:#FDE68A;">悟堂 · 今日觉察牌</span>
                <span class="tap-hint card-back-flip-btn" style="margin-top:6px;font-size:11px;">点击翻开这张牌 ↺</span>
              </div>
            </div>

            <!-- 卡面 (正面：纯粹优雅，无冗余按钮遮挡，留出安全边距) -->
            <div class="awareness-card-face awareness-card-front">
              <div class="awareness-card-content">
                <div class="card-front-title" id="awFrontTitle">总想让所有人满意</div>
                <div class="card-front-question serif" id="awFrontQuestion">「我是不是很久没有认真问过自己，真正想要的是什么？」</div>
                <div class="card-front-desc" id="awFrontDesc">这是一张用于自我反思的提示卡，不代表对你的判断。</div>
              </div>
              <div class="card-front-flip-tip">轻触卡片可翻转 ↺</div>
            </div>
          </div>

          <!-- 觉察交互底栏 (独立于卡面正下方，视觉轻盈、不挡卡牌) -->
          <div class="awareness-controls-dock">
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
        </div>"""

new_html_block = """        <div class="awareness-stage awareness-split-stage">
          <!-- 左侧：图卡 (纯净水彩画卷，无文字遮挡) -->
          <div class="awareness-card-column">
            <div class="awareness-card-container" id="awarenessCardBox" title="点击翻转卡牌">
              <!-- 卡背 (3D 动态金色天体罗盘) -->
              <div class="awareness-card-face awareness-card-back card-3d-back">
                <div class="card-corner tl"></div>
                <div class="card-corner tr"></div>
                <div class="card-corner bl"></div>
                <div class="card-corner br"></div>
                <div class="card-back-header">SUBCONSCIOUS</div>
                <div class="card-back-center" style="height:170px;">
                  <div class="card-orbit-ring" style="width:140px;height:140px;"></div>
                  <div class="card-orbit-ring-inner" style="width:105px;height:105px;"></div>
                  <div class="card-starburst">
                    <div class="card-starburst-ray v" style="height:64px;"></div>
                    <div class="card-starburst-ray h" style="width:64px;"></div>
                    <div class="card-starburst-ray d1" style="height:48px;"></div>
                    <div class="card-starburst-ray d2" style="height:48px;"></div>
                    <div class="card-core-gem" style="width:34px;height:34px;font-size:16px;">悟</div>
                  </div>
                </div>
                <div class="card-back-footer">
                  <span style="font-size:14px;font-weight:600;color:#FDE68A;">悟堂 · 今日觉察牌</span>
                  <span class="tap-hint card-back-flip-btn" style="margin-top:6px;font-size:11px;">点击翻开这张牌 ↺</span>
                </div>
              </div>

              <!-- 卡面 (正面：纯粹水彩画卷，无任何文字遮挡) -->
              <div class="awareness-card-face awareness-card-front">
                <div class="card-front-flip-tip">轻触卡片可翻转 ↺</div>
              </div>
            </div>
          </div>

          <!-- 右侧：文字卡片 (字卡 · 觉察反思与交互引导) -->
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
          </div>
        </div>"""

assert old_html_block in text, "old_html_block not found!"
text = text.replace(old_html_block, new_html_block, 1)

with open(template_path, "w", encoding="utf-8") as f:
    f.write(text)

print("[SUCCESS] Split layout applied to _template.html successfully!")
