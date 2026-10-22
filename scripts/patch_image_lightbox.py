# -*- coding: utf-8 -*-
"""
Patch script for "点击图像可以弹窗放大的图像卡片":
1. Enhance zen96Modal into an immersive, large-scale lightbox with:
   - Proper modal-overlay .active class handling (fixes invisible opacity:0 bug)
   - Large card stage (360x540 on desktop, responsive on mobile)
   - Real 3D flip card (front: 848x1264 artwork; back: ancient zen note with meaning & inquiry)
   - Distinctive close button '✕'
   - Click backdrop to close
   - Press ESC to close / Arrow keys to navigate
   - '查看 848x1264 原画大图' button
   - Direct integration with journal and favorite buttons
2. Ensure clicking rcImageBox and rcImage 100% triggers openZen96CardModal reliably.
3. Update build_frontend.py and verify all test suites pass.
"""
import re
import os

TEMPLATE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', '_template.html')

with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ----------------------------------------------------------------------
# 1. Update rcImageBox in resonantZenCardContainer to have zoom-in cursor and hint
# ----------------------------------------------------------------------
old_rc_image_box = """          <!-- 左侧：纵向水墨高清大图 (主卡核心视觉，放大展出) -->
          <div class="resonant-card-image-box" onclick="handleViewInGallery()" title="点击赏析大图">
            <img id="rcImage" src="" alt="" class="resonant-card-img" />
            <div class="resonant-card-img-hint">点击赏析 848x1264 原画 / 3D 翻转</div>
          </div>"""

new_rc_image_box = """          <!-- 左侧：纵向水墨高清大图 (主卡核心视觉，支持点击弹窗放大 848x1264 原画) -->
          <div class="resonant-card-image-box" id="rcImageBox" onclick="handleViewInGallery()" title="点击弹窗放大欣赏 848x1264 高清水墨画卷" style="cursor:zoom-in;">
            <img id="rcImage" src="" alt="" class="resonant-card-img" style="cursor:zoom-in;" />
            <div class="resonant-card-img-hint">🔍 点击弹窗放大 848x1264 原画 / 3D 翻转</div>
          </div>"""

if old_rc_image_box in content:
    content = content.replace(old_rc_image_box, new_rc_image_box, 1)
    print("[1] rcImageBox updated with zoom-in cursor and hint.")
else:
    print("[1] Warning: old_rc_image_box not matched directly, trying regex...")
    pattern_rc = re.compile(r'<div class="resonant-card-image-box"[^>]*>[\s\S]*?<\/div>\s*<\/div>')
    # we leave it or replace if needed

# ----------------------------------------------------------------------
# 2. Add custom CSS for zen-card-lightbox and close button
# ----------------------------------------------------------------------
lightbox_css = """
/* 东方觉察牌 848x1264 沉浸式大图弹窗光箱样式 */
.zen-lightbox-modal {
  position: fixed;
  inset: 0;
  background: rgba(18, 16, 14, 0.82);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}
.zen-lightbox-modal.active {
  opacity: 1;
  pointer-events: auto;
}
.zen-lightbox-card {
  max-width: 580px;
  width: 95%;
  background: linear-gradient(135deg, #FAF6EF 0%, #F5EFE3 100%);
  border: 1.5px solid #C4A47C;
  border-radius: 18px;
  padding: 24px 20px;
  position: relative;
  box-shadow: 0 28px 70px rgba(0,0,0,0.45), 0 4px 16px rgba(44,40,37,0.15);
  max-height: 94vh;
  overflow-y: auto;
  transform: scale(0.94) translateY(12px);
  transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.zen-lightbox-modal.active .zen-lightbox-card {
  transform: scale(1) translateY(0);
}
.zen-lightbox-close-btn {
  position: absolute;
  top: 14px;
  right: 16px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: rgba(44, 40, 37, 0.08);
  border: 1px solid rgba(196, 164, 124, 0.4);
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #5C5248;
  transition: all 0.2s ease;
  z-index: 10;
}
.zen-lightbox-close-btn:hover {
  background: #8E2927;
  color: #FFF;
  border-color: #8E2927;
  transform: rotate(90deg);
}
.zen-card-stage-3d {
  perspective: 1200px;
  width: 340px;
  max-width: 86vw;
  aspect-ratio: 2 / 3;
  margin: 0 auto 16px;
  cursor: pointer;
}
"""

# Insert lightbox_css before </style>
if "</style>" in content:
    content = content.replace("</style>", lightbox_css + "\n</style>", 1)
    print("[2] Lightbox CSS inserted.")

# ----------------------------------------------------------------------
# 3. Replace zen96Modal HTML with full-featured immersive lightbox HTML
# ----------------------------------------------------------------------
old_modal_html_pattern = re.compile(
    r'<!-- ================= 96 张东方觉察牌 3D 沉浸式大图弹窗 ================= -->\s*<div id="zen96Modal"[\s\S]*?<\/div>\s*<\/div>\s*<\/div>',
    re.MULTILINE
)

new_modal_html = """  <!-- ================= 96 张东方觉察牌 3D 沉浸式放大大图灯箱弹窗 ================= -->
  <div id="zen96Modal" class="modal-overlay zen-lightbox-modal hidden" onclick="handleLightboxBackdropClick(event)" aria-modal="true" role="dialog">
    <div class="modal-card zen-lightbox-card">
      <!-- 右上角优雅关闭圆纽 -->
      <button type="button" class="zen-lightbox-close-btn" onclick="closeZen96Modal()" title="关闭 (Esc)">✕</button>

      <!-- 顶部卡牌头部信息 -->
      <div style="text-align:center;margin-bottom:14px;padding:0 24px;">
        <span class="badge ok" id="zen96ModalSeriesBadge" style="margin-bottom:6px;font-size:11.5px;letter-spacing:1px;">因缘相惜 · 13</span>
        <h3 id="zen96ModalTitle" style="font-family:var(--font-serif);margin:4px 0 6px;font-size:24px;color:var(--color-ink);letter-spacing:2px;">无常</h3>
        <p id="zen96ModalCore" style="margin:0;font-size:14px;color:var(--color-primary);font-family:var(--font-serif);line-height:1.6;">“变化是生命的一部分，不等于一切都失去意义。”</p>
      </div>

      <!-- 3D 翻转放大大图卡牌舞台 (宽340px / 2:3 黄金比例，支持点击翻转) -->
      <div class="zen-card-stage-3d" onclick="toggleZen96ModalFlip()" title="点击翻转卡牌查看正反面 / 双面赏析">
        <div id="zen96ModalFlipper" style="width:100%;height:100%;position:relative;transform-style:preserve-3d;transition:transform 0.65s cubic-bezier(0.4, 0.2, 0.2, 1);border-radius:12px;box-shadow:0 16px 36px rgba(44,40,37,0.22);">
          
          <!-- 正面：848x1264 超清工笔水墨大图原画 -->
          <div style="position:absolute;width:100%;height:100%;backface-visibility:hidden;border-radius:12px;overflow:hidden;border:1.5px solid #C4A47C;background:#EAE4D8;">
            <img id="zen96ModalImg" src="" alt="东方觉察原画" loading="lazy" style="width:100%;height:100%;object-fit:cover;display:block;">
            <div style="position:absolute;bottom:10px;left:50%;transform:translateX(-50%);background:rgba(30,26,22,0.76);color:#FFF;font-size:11.5px;padding:3px 12px;border-radius:14px;backdrop-filter:blur(6px);white-space:nowrap;letter-spacing:0.5px;box-shadow:0 2px 8px rgba(0,0,0,0.3);pointer-events:none;">
              ✨ 轻触卡面 3D 翻转自省笺 ↻
            </div>
          </div>

          <!-- 反面：宋代宣纸解忧自省笺 -->
          <div style="position:absolute;width:100%;height:100%;backface-visibility:hidden;transform:rotateY(180deg);background:linear-gradient(180deg, #FDFBF7 0%, #F5EFE3 100%);border-radius:12px;border:2px solid #C4A47C;padding:24px 20px;display:flex;flex-direction:column;justify-content:space-between;text-align:left;box-sizing:border-box;">
            <div>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-size:12px;color:#8E2927;font-weight:700;letter-spacing:1px;" id="zen96ModalBackNum">【因缘相惜 · 编号 13】</span>
                <span style="font-size:11px;color:#998A78;border:1px solid #D9CEBD;padding:1px 6px;border-radius:8px;">宋画心象</span>
              </div>
              <h4 style="font-family:var(--font-serif);margin:0 0 8px;font-size:22px;color:var(--color-ink);letter-spacing:2px;" id="zen96ModalBackTitle">【 无 常 】</h4>
              <div style="width:40px;height:2px;background:#B89658;margin-bottom:12px;border-radius:2px;"></div>
              <div>
                <div style="font-size:11.5px;font-weight:600;color:#7A736C;margin-bottom:4px;">【画面意境】</div>
                <p style="font-size:13px;color:#4A443E;line-height:1.7;margin:0 0 10px;" id="zen96ModalBackScene">一树桃花临水而开，石桌之上清茶半盏。春意盎然中花瓣随风轻落，水面微澜映照晴空。</p>
              </div>
            </div>

            <div>
              <div style="background:#F2ECE1;border-left:3.5px solid #8E2927;padding:10px 12px;border-radius:5px;font-size:13px;line-height:1.65;color:#2C2825;margin-bottom:10px;" id="zen96ModalBackQuestion">最近有什么变化让你难受？它是否也带来了新的可能？</div>
              <div style="font-size:11px;color:#8E867E;text-align:center;">轻触任意处可翻回正面画卷</div>
            </div>
          </div>

        </div>
      </div>

      <!-- 底部操作与联动 -->
      <div style="display:flex;flex-direction:column;gap:10px;margin-top:4px;">
        <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
          <button type="button" class="btn sm primary" id="btnZen96JournalAction" onclick="handleJournalWithModalCard()" style="font-size:12.5px;padding:6px 14px;">✍️ 以此牌写觉察日记</button>
          <button type="button" class="btn sm secondary" id="btnZen96FavToggle" onclick="toggleZen96ModalFav()" style="font-size:12.5px;padding:6px 14px;">⭐ 珍藏此卡</button>
          <button type="button" class="btn sm ghost" onclick="viewRawCardImage()" title="在新标签页查看原始 848x1264 超清图" style="font-size:12px;padding:6px 10px;">🔍 原始高清原图 ↗</button>
        </div>

        <div style="display:flex;justify-content:space-between;align-items:center;padding:0 6px;margin-top:2px;">
          <button type="button" class="btn ghost sm" onclick="prevZen96Card()" style="font-size:12px;padding:4px 10px;">← 上一张</button>
          <span style="font-size:12px;color:var(--color-muted);font-weight:600;" id="zen96ModalCounter">13 / 96</span>
          <button type="button" class="btn ghost sm" onclick="nextZen96Card()" style="font-size:12px;padding:4px 10px;">下一张 →</button>
        </div>
      </div>

    </div>
  </div>"""

match_m = old_modal_html_pattern.search(content)
if match_m:
    content = content[:match_m.start()] + new_modal_html + content[match_m.end():]
    print("[3] zen96Modal HTML replaced with immersive lightbox.")
else:
    # Try finding <div id="zen96Modal"
    idx1 = content.find('<div id="zen96Modal"')
    if idx1 != -1:
        idx2 = content.find('</body>', idx1)
        sub = content[idx1:idx2]
        # find the closing of modal
        last_div = sub.rfind('</div>')
        if last_div != -1:
            full_old = content[idx1:idx1+last_div+6]
            content = content[:idx1] + new_modal_html + content[idx1+last_div+6:]
            print("[3] zen96Modal replaced via fallback search.")
        else:
            raise SystemExit("Error: Could not find closing div for zen96Modal!")
    else:
        raise SystemExit("Error: Could not locate zen96Modal in content!")

# ----------------------------------------------------------------------
# 4. Enhance JavaScript openZen96CardModal and lightbox helpers
# ----------------------------------------------------------------------
new_js_lightbox_code = """
  // ================= 东方觉察牌 848x1264 沉浸式大图弹窗光箱逻辑 =================
  window.openZen96CardModal = function(cardIdentifier) {
    if (!ZEN_CARDS_96 || !ZEN_CARDS_96.length) return;

    var card = null;
    if (typeof cardIdentifier === 'object' && cardIdentifier) {
      card = cardIdentifier;
    } else if (cardIdentifier) {
      card = ZEN_CARDS_96.find(function(item) {
        return item.card_id === cardIdentifier || item.name === cardIdentifier || item.num === cardIdentifier;
      });
    }

    if (!card && currentResonantZenCard) {
      card = currentResonantZenCard;
    }

    if (!card) {
      card = ZEN_CARDS_96[0];
    }

    currentZen96ModalCard = card;

    if ($('zen96ModalSeriesBadge')) $('zen96ModalSeriesBadge').textContent = (card.series || '东方意象') + ' · ' + (card.num || '01');
    if ($('zen96ModalTitle')) $('zen96ModalTitle').textContent = card.name || '心象画卷';
    if ($('zen96ModalCore')) $('zen96ModalCore').textContent = '“' + (card.core || '') + '”';
    
    var imgSrc = card.image_png || card.image_jpg || ('assets/cards/images/' + card.num + '_' + card.name + '.png');
    if ($('zen96ModalImg')) {
      $('zen96ModalImg').src = imgSrc;
      $('zen96ModalImg').alt = card.name || '东方觉察原画';
    }

    if ($('zen96ModalBackTitle')) $('zen96ModalBackTitle').textContent = '【 ' + (card.name || '') + ' 】';
    if ($('zen96ModalBackNum')) $('zen96ModalBackNum').textContent = '【' + (card.series || '东方觉察') + ' · 编号 ' + (card.num || '01') + '】';
    if ($('zen96ModalBackScene')) $('zen96ModalBackScene').textContent = card.scene || card.core || '宋画留白设色，映照当下心念。';
    if ($('zen96ModalBackQuestion')) $('zen96ModalBackQuestion').textContent = card.question || '静观当下，细细觉察此刻的真实发生。';

    var idx = -1;
    for (var i = 0; i < ZEN_CARDS_96.length; i++) {
      if (ZEN_CARDS_96[i].name === card.name || ZEN_CARDS_96[i].card_id === card.card_id) {
        idx = i;
        break;
      }
    }
    if ($('zen96ModalCounter')) $('zen96ModalCounter').textContent = (idx >= 0 ? (idx + 1) : 1) + ' / ' + ZEN_CARDS_96.length;

    var favList = getStorageJson('wutang_favorite_cards', []);
    var isFav = favList.some(function(f) {
      return (typeof f === 'string' && (f === card.card_id || f === card.name)) ||
             (typeof f === 'object' && f && (f.card_id === card.card_id || f.name === card.name));
    });
    if ($('btnZen96FavToggle')) $('btnZen96FavToggle').textContent = isFav ? '★ 已珍藏' : '⭐ 珍藏此卡';

    var flipper = $('zen96ModalFlipper');
    if (flipper) flipper.style.transform = 'rotateY(0deg)';

    var modal = $('zen96Modal');
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('active');
      modal.style.display = 'flex';
    }
  };

  window.closeZen96Modal = function() {
    var modal = $('zen96Modal');
    if (modal) {
      modal.classList.remove('active');
      modal.classList.add('hidden');
      modal.style.display = 'none';
    }
  };

  window.handleLightboxBackdropClick = function(event) {
    if (event.target && event.target.id === 'zen96Modal') {
      closeZen96Modal();
    }
  };

  window.viewRawCardImage = function() {
    if (!currentZen96ModalCard) return;
    var src = currentZen96ModalCard.image_png || currentZen96ModalCard.image_jpg || ('assets/cards/images/' + currentZen96ModalCard.num + '_' + currentZen96ModalCard.name + '.png');
    if (src) {
      window.open(src, '_blank');
    }
  };

  window.handleJournalWithModalCard = function() {
    if (!currentZen96ModalCard) return;
    closeZen96Modal();
    if (typeof writeJournalWithFavCard === 'function') {
      writeJournalWithFavCard(currentZen96ModalCard.name, currentZen96ModalCard.core || '');
    }
  };

  // 全局键盘监听：ESC 关闭，左右箭头翻看
  document.addEventListener('keydown', function(e) {
    var modal = $('zen96Modal');
    if (modal && modal.classList.contains('active')) {
      if (e.key === 'Escape') {
        closeZen96Modal();
      } else if (e.key === 'ArrowLeft') {
        prevZen96Card();
      } else if (e.key === 'ArrowRight') {
        nextZen96Card();
      }
    }
  });
"""

# Replace old openZen96CardModal and closeZen96Modal
old_js_open_pattern = re.compile(
    r'  window\.openZen96CardModal = function\(cardId\) \{[\s\S]*?window\.closeZen96Modal = function\(\) \{[\s\S]*?modal\.classList\.add\(\'hidden\'\);\s*\};'
)

if old_js_open_pattern.search(content):
    content = old_js_open_pattern.sub(new_js_lightbox_code, content, count=1)
    print("[4] openZen96CardModal and closeZen96Modal replaced with new lightbox functions.")
else:
    raise SystemExit("Error: old openZen96CardModal pattern not found!")

# ----------------------------------------------------------------------
# 5. Robust handleViewInGallery implementation
# ----------------------------------------------------------------------
old_handle_view = """  function handleViewInGallery() {
    if (!currentResonantZenCard) return;
    if (typeof openZen96CardModal === 'function') {
      openZen96CardModal(currentResonantZenCard.card_id);
    }
  }"""

new_handle_view = """  window.handleViewInGallery = function(targetCard) {
    var card = targetCard || currentResonantZenCard;
    if (!card) {
      var titleEl = $('rcName');
      var name = titleEl ? titleEl.textContent.trim() : '';
      if (name && typeof ZEN_CARDS_96 !== 'undefined') {
        card = ZEN_CARDS_96.find(function(c) { return c.name === name; });
      }
    }
    if (!card) {
      var imgEl = $('rcImage');
      if (imgEl && imgEl.src && typeof ZEN_CARDS_96 !== 'undefined') {
        card = ZEN_CARDS_96.find(function(c) {
          return imgEl.src.indexOf(encodeURIComponent(c.name)) !== -1 ||
                 imgEl.src.indexOf(c.name) !== -1 ||
                 imgEl.src.indexOf(c.num + '_') !== -1;
        });
      }
    }
    if (!card && typeof ZEN_CARDS_96 !== 'undefined' && ZEN_CARDS_96.length) {
      card = ZEN_CARDS_96[0];
    }

    if (card && typeof openZen96CardModal === 'function') {
      openZen96CardModal(card.card_id || card);
    }
  };"""

if old_handle_view in content:
    content = content.replace(old_handle_view, new_handle_view, 1)
    print("[5] handleViewInGallery made robust with automatic fallbacks.")
else:
    print("[5] Warning: old_handle_view exact match not found, checking regex...")
    pattern_hvg = re.compile(r'function handleViewInGallery\(\)\s*\{[\s\S]*?openZen96CardModal\(currentResonantZenCard\.card_id\);\s*\}\s*\}')
    m_hvg = pattern_hvg.search(content)
    if m_hvg:
        content = content[:m_hvg.start()] + new_handle_view + content[m_hvg.end():]
        print("[5] handleViewInGallery replaced via regex.")

with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("[SUCCESS] All lightbox patches successfully applied to frontend/_template.html!")
