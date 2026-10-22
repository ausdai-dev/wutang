# -*- coding: utf-8 -*-
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_path = os.path.join(ROOT, "frontend", "_template.html")

with open(template_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update .awareness-card-front CSS to showcase the OH-card watercolor painting
old_css_front = """.awareness-card-front {
  background: #FFFFFF;
  transform: rotateY(180deg);
  text-align: center;
  padding: 68px 24px 44px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  background-size: 100% 100%;
  background-repeat: no-repeat;
}"""

new_css_front = """.awareness-card-front {
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

assert old_css_front in text, "old_css_front not found!"
text = text.replace(old_css_front, new_css_front, 1)

# 2. Update .awareness-card-content CSS to frosted parchment glass dock
old_css_content = """.awareness-card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
}"""

new_css_content = """.awareness-card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(254, 252, 248, 0.90);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  padding: 16px 14px 14px;
  border: 1px solid rgba(217, 206, 189, 0.7);
  box-shadow: 0 6px 20px rgba(35, 30, 25, 0.12);
  margin-bottom: 8px;
}"""

assert old_css_content in text, "old_css_content not found!"
text = text.replace(old_css_content, new_css_content, 1)

# 3. Update renderAwarenessCard to use card.image_png
old_render_front = """      var frontEl = cardBox.querySelector('.awareness-card-front');
      if (frontEl) {
        frontEl.style.backgroundImage = 'url(' + getCardAsset('card_mindset', 'front') + ')';
        frontEl.style.backgroundSize = '100% 100%';
        frontEl.style.backgroundRepeat = 'no-repeat';
        frontEl.style.border = 'none';
      }"""

new_render_front = """      var frontEl = cardBox.querySelector('.awareness-card-front');
      if (frontEl) {
        var imgSrc = card.image_png || ('assets/cards/mindset/' + (card.card_id || 'M-001') + '.png');
        frontEl.style.backgroundImage = 'url(' + imgSrc + ')';
        frontEl.style.backgroundSize = 'cover';
        frontEl.style.backgroundPosition = 'center';
        frontEl.style.border = 'none';
      }"""

assert old_render_front in text, "old_render_front not found!"
text = text.replace(old_render_front, new_render_front, 1)

# 4. Update renderStudioCards to show watercolor preview for mindset cards
old_studio_mindset = """    if (typeFilter === 'all' || typeFilter === 'mindset') {
      CARDS_MINDSET.forEach(function(c) {
        cards.push({
          type: 'mindset',
          typeLabel: '01 心境',
          id: c.card_id || c.id,
          title: c.title,
          quote: '「' + (c.front_text || c.quote || '') + '」',
          desc: c.short_description || c.sample_prompt || c.subtitle,
          meta: '标签：' + (c.theme_tags || c.scenarios || []).join(' · '),
          statusBadge: '<span class="badge ok">MVP 齐备</span>'
        });
      });
    }"""

new_studio_mindset = """    if (typeFilter === 'all' || typeFilter === 'mindset') {
      CARDS_MINDSET.forEach(function(c) {
        var imgSrc = c.image_png || ('assets/cards/mindset/' + (c.card_id || 'M-001') + '.png');
        cards.push({
          type: 'mindset',
          typeLabel: '01 觉察 · 欧卡',
          id: c.card_id || c.id,
          title: c.title,
          image: imgSrc,
          quote: '「' + (c.front_text || c.quote || '') + '」',
          desc: c.short_description || c.sample_prompt || c.subtitle,
          meta: '标签：' + (c.theme_tags || c.scenarios || []).join(' · '),
          statusBadge: '<span class="badge ok">欧卡水彩</span>'
        });
      });
    }"""

if old_studio_mindset in text:
    text = text.replace(old_studio_mindset, new_studio_mindset, 1)
    # Also update mapping to output image if present
    old_card_cell = """        + '<div class="serif" style="font-size:16px;font-weight:600;color:var(--color-ink);margin-bottom:6px;">' + esc(c.title) + '</div>'"""
    new_card_cell = """        + (c.image ? '<div style="width:100%;height:140px;margin-bottom:10px;border-radius:6px;overflow:hidden;background:#FAF6EF;"><img src="' + c.image + '" alt="' + esc(c.title) + '" style="width:100%;height:100%;object-fit:cover;"></div>' : '')\n        + '<div class="serif" style="font-size:16px;font-weight:600;color:var(--color-ink);margin-bottom:6px;">' + esc(c.title) + '</div>'"""
    if old_card_cell in text:
        text = text.replace(old_card_cell, new_card_cell, 1)

with open(template_path, "w", encoding="utf-8") as f:
    f.write(text)

print("[SUCCESS] _template.html updated with OH-card watercolor styling!")
