# -*- coding: utf-8 -*-
import sys

with open('frontend/_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS
old_css = """.resonant-card-section {
  margin: 32px 0 24px;
  animation: fadeIn 0.5s ease-out;
}
.resonant-card-card {
  background: rgba(253, 251, 247, 0.96);
  border: 1px solid #D9CEBD;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 10px 28px rgba(44, 40, 37, 0.06);
  display: flex;
  gap: 22px;
  align-items: stretch;
  position: relative;
  overflow: hidden;
}
.resonant-card-image-box {
  width: 170px;
  min-width: 170px;
  aspect-ratio: 2 / 3;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
  border: 1.5px solid #C4A47C;
  box-shadow: 0 6px 18px rgba(44, 40, 37, 0.12);
  cursor: pointer;
  background: #EAE4D8;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.resonant-card-image-box:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(44, 40, 37, 0.2);
}
.resonant-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.resonant-card-img-hint {
  position: absolute;
  bottom: 8px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(42, 38, 35, 0.75);
  color: #FFF;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  backdrop-filter: blur(4px);
  white-space: nowrap;
  pointer-events: none;
}
.resonant-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}
.resonant-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 10px;
  border-bottom: 1px dashed #E2DACB;
  padding-bottom: 8px;
}
.resonant-card-series {
  font-size: 11.5px;
  background: #EBF3ED;
  color: #2B6E3F;
  border: 1px solid rgba(43, 110, 63, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
  margin-right: 6px;
}
.resonant-card-no {
  font-size: 11.5px;
  color: #7E7870;
  font-family: monospace;
}
.resonant-card-title {
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 700;
  color: #8E2927;
  margin: 0;
  letter-spacing: 2px;
}
.resonant-card-core-box,
.resonant-card-question-box,
.resonant-card-reason-box {
  margin-bottom: 8px;
  line-height: 1.55;
}
.rc-label {
  font-size: 11.5px;
  font-weight: 700;
  color: #7A736C;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}
.rc-core-text {
  font-family: var(--font-serif);
  font-size: 14.5px;
  color: var(--color-ink);
  font-weight: 600;
}
.rc-question-text {
  font-size: 13.5px;
  color: #2B6E3F;
  background: rgba(235, 243, 237, 0.5);
  border-left: 3px solid #2B6E3F;
  padding: 5px 10px;
  border-radius: 0 4px 4px 0;
}
.rc-reason-text {
  font-size: 12.5px;
  color: #6A635B;
  font-style: italic;
}
.resonant-card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #E2DACB;
}
.btn-rc-action {
  background: #FFF;
  border: 1px solid #D9CEBD;
  color: #4A443E;
  padding: 6px 12px;
  border-radius: 18px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
}
.btn-rc-action:hover {
  border-color: #8E2927;
  color: #8E2927;
  background: #FAF5F5;
  transform: translateY(-1px);
}
.btn-rc-action.primary {
  background: #2B6E3F;
  color: #FFF;
  border-color: #2B6E3F;
}
.btn-rc-action.primary:hover {
  background: #235B34;
  color: #FFF;
}
@media (max-width: 640px) {
  .resonant-card-card {
    flex-direction: column;
    align-items: center;
  }
  .resonant-card-image-box {
    width: 200px;
  }
}"""

new_css = """.resonant-card-section {
  margin: 22px 0 30px;
  animation: fadeIn 0.5s ease-out;
}
.resonant-card-card {
  background: linear-gradient(135deg, rgba(255, 253, 249, 0.98) 0%, rgba(248, 243, 233, 0.95) 100%);
  border: 1.5px solid #D4C5B0;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 16px 40px rgba(44, 40, 37, 0.08), 0 0 0 1px rgba(196, 164, 124, 0.25);
  display: flex;
  gap: 32px;
  align-items: stretch;
  position: relative;
  overflow: hidden;
}
.resonant-card-image-box {
  width: 320px;
  min-width: 320px;
  max-width: 340px;
  aspect-ratio: 2 / 3;
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  border: 2.5px solid #C4A47C;
  box-shadow: 0 16px 36px rgba(44, 40, 37, 0.18), 0 0 0 4px rgba(196, 164, 124, 0.2);
  cursor: pointer;
  background: #EAE4D8;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease;
  flex-shrink: 0;
}
.resonant-card-image-box:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 48px rgba(44, 40, 37, 0.24), 0 0 0 5px rgba(196, 164, 124, 0.35);
}
.resonant-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.5s ease;
}
.resonant-card-image-box:hover .resonant-card-img {
  transform: scale(1.02);
}
.resonant-card-img-hint {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(36, 32, 28, 0.85);
  color: #FFF;
  font-size: 11.5px;
  font-weight: 500;
  padding: 4px 14px;
  border-radius: 14px;
  backdrop-filter: blur(6px);
  white-space: nowrap;
  pointer-events: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.18);
  letter-spacing: 0.5px;
}
.resonant-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
}
.resonant-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  border-bottom: 1px dashed #E2DACB;
  padding-bottom: 10px;
}
.resonant-card-series {
  font-size: 13px;
  background: #EBF3ED;
  color: #2B6E3F;
  border: 1px solid rgba(43, 110, 63, 0.25);
  padding: 3px 12px;
  border-radius: 14px;
  font-weight: 600;
  margin-right: 8px;
}
.resonant-card-no {
  font-size: 12.5px;
  color: #7E7870;
  font-family: monospace;
}
.resonant-card-title {
  font-family: var(--font-serif);
  font-size: 34px;
  font-weight: 700;
  color: #8E2927;
  margin: 0;
  letter-spacing: 4px;
}
.resonant-card-core-box {
  background: rgba(254, 250, 244, 0.95);
  border-left: 4px solid #B89658;
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  margin-bottom: 10px;
  box-shadow: 0 2px 6px rgba(184, 150, 88, 0.06);
}
.resonant-card-question-box {
  background: rgba(240, 247, 243, 0.95);
  border-left: 4px solid #2B6E3F;
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  margin-bottom: 10px;
  box-shadow: 0 2px 6px rgba(43, 110, 63, 0.05);
}
.resonant-card-reason-box {
  background: rgba(255, 255, 255, 0.7);
  border-left: 3px solid #8E867E;
  padding: 10px 14px;
  border-radius: 0 6px 6px 0;
  margin-bottom: 12px;
}
.rc-label {
  font-size: 12px;
  font-weight: 700;
  color: #7A736C;
  letter-spacing: 0.8px;
  margin-bottom: 3px;
}
.rc-core-text {
  font-family: var(--font-serif);
  font-size: 16px;
  color: var(--color-ink);
  font-weight: 600;
  line-height: 1.6;
}
.rc-question-text {
  font-size: 14.5px;
  color: #1E512E;
  font-family: var(--font-serif);
  line-height: 1.6;
}
.rc-reason-text {
  font-size: 13px;
  color: #554E46;
  line-height: 1.65;
}
.resonant-card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed #E2DACB;
}
.btn-rc-action {
  background: #FFF;
  border: 1px solid #D9CEBD;
  color: #4A443E;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}
.btn-rc-action:hover {
  border-color: #8E2927;
  color: #8E2927;
  background: #FAF5F5;
  transform: translateY(-1px);
}
.btn-rc-action.primary {
  background: linear-gradient(135deg, #2B6E3F, #235B34);
  color: #FFF;
  border-color: #235B34;
  box-shadow: 0 4px 12px rgba(43, 110, 63, 0.25);
}
.btn-rc-action.primary:hover {
  background: linear-gradient(135deg, #235B34, #1B4728);
  color: #FFF;
  transform: translateY(-1px);
}
@media (max-width: 820px) {
  .resonant-card-card {
    flex-direction: column;
    align-items: center;
    gap: 18px;
    padding: 18px;
  }
  .resonant-card-image-box {
    width: 280px;
    min-width: 0;
    max-width: 90%;
  }
}"""

if old_css in content:
    content = content.replace(old_css, new_css, 1)
    print("CSS updated successfully")
else:
    print("Warning: old_css not found")

# 2. Extract resonantZenCardContainer and liberationHeroContainer
# Let's find their blocks
import re

dom_old_pattern = r'''(      <!-- PRD 4\.0 专属解脱之道 3D 卡牌舞台 -->\s*<div id="liberationHeroContainer"[\s\S]*?<\/div>\s*<\/div>\s*)(      <!-- PRD 4\.1 借境观心 · 契合心象画卷 \(96张典藏觉察牌联动\) -->\s*<div id="resonantZenCardContainer" class="resonant-card-section hidden">[\s\S]*?<\/div>\s*<\/div>\s*<\/div>)'''

match = re.search(dom_old_pattern, content)
if match:
    lib_block = match.group(1)
    res_block = match.group(2)
    
    # Update header in res_block to highlight 【本页主卡】
    res_block_updated = res_block.replace(
        '<span>🖼️ 借境观心 · 契合心象画卷</span>\n            <span style="font-size:12px;font-weight:normal;color:var(--color-muted);">先圣映照的当下意象</span>',
        '<span>🖼️ 借境观心 · 契合心象画卷</span>\n            <span style="font-size:12px;font-weight:700;color:#FFF;background:linear-gradient(135deg, #8E2927, #B83A38);padding:2px 9px;border-radius:12px;box-shadow:0 2px 6px rgba(142,41,39,0.25);letter-spacing:1px;">本页主卡</span>\n            <span style="font-size:12.5px;font-weight:normal;color:var(--color-muted);">先圣映照的当下第一心象</span>'
    )
    res_block_updated = res_block_updated.replace(
        '<!-- 左侧：2:3 纵向水墨大图，可点击查看大图 -->',
        '<!-- 左侧：纵向水墨高清大图 (主卡核心视觉，放大展出) -->'
    )
    res_block_updated = res_block_updated.replace(
        '<div class="resonant-card-img-hint">点击赏析大图</div>',
        '<div class="resonant-card-img-hint">✨ 点击赏析 848x1264 原画 / 3D 翻转</div>'
    )
    res_block_updated = res_block_updated.replace(
        '<!-- PRD 4.1 借境观心 · 契合心象画卷 (96张典藏觉察牌联动) -->',
        '<!-- PRD 4.1 借境观心 · 契合心象画卷 (本页主卡 · 96张东方智慧觉察牌) -->'
    )
    
    # Swap order: resonant first, liberation second!
    new_combined = res_block_updated + "\n\n" + lib_block
    content = content.replace(match.group(0), new_combined, 1)
    print("DOM order swapped successfully: resonantZenCardContainer is now BEFORE liberationHeroContainer")
else:
    print("Warning: DOM pattern match failed")

with open('frontend/_template.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Finished patch.")
