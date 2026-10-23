# -*- coding: utf-8 -*-
"""
补丁脚本：将悟堂首页静态禅茶横幅升级为 5 大东方心境画卷平滑轮播组件 (Zen Banner Carousel)
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

def main():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 替换 CSS
    m_css = re.search(r'/\* 首页禅茶意境横幅 \*/.*?@media \(max-width: 600px\) \{.*?\.zen-tea-banner \{ height: 120px; \}\s*\}', content, re.DOTALL)
    if not m_css:
        raise RuntimeError("CSS anchor for banner not found")

    new_css = """/* ================= 首页东方心境画卷轮播 Banner (Zen Carousel) ================= */
.zen-carousel-container {
  position: relative;
  width: 100%;
  height: 168px;
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 20px;
  border: 1px solid var(--color-border);
  box-shadow: 0 4px 18px rgba(34, 31, 27, 0.05);
  background: #F4EFE6;
  user-select: none;
}

@media (max-width: 600px) {
  .zen-carousel-container {
    height: 125px;
    border-radius: 10px;
    margin-bottom: 16px;
  }
}

.zen-carousel-slides {
  position: relative;
  width: 100%;
  height: 100%;
}

.zen-carousel-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.85s cubic-bezier(0.25, 1, 0.5, 1), transform 1.2s cubic-bezier(0.25, 1, 0.5, 1);
  transform: scale(1.02);
  cursor: pointer;
}

.zen-carousel-slide.active {
  opacity: 1;
  visibility: visible;
  transform: scale(1);
  z-index: 2;
}

.zen-carousel-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  display: block;
  filter: saturate(0.94) brightness(0.97);
}

/* 左右轻巧翻页控制箭头 (悬停时显现) */
.zen-carousel-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(253, 251, 248, 0.82);
  border: 1px solid rgba(232, 226, 214, 0.9);
  color: var(--color-ink);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 5;
  opacity: 0;
  transition: all var(--trans);
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  outline: none;
}

.zen-carousel-container:hover .zen-carousel-arrow {
  opacity: 0.88;
}

.zen-carousel-arrow:hover {
  opacity: 1 !important;
  background: #FFFFFF;
  color: var(--color-primary);
  transform: translateY(-50%) scale(1.1);
}

.zen-carousel-arrow.prev { left: 10px; }
.zen-carousel-arrow.next { right: 10px; }

/* 底部胶囊指示点 */
.zen-carousel-dots {
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 6px;
  z-index: 5;
  background: rgba(34, 31, 27, 0.28);
  padding: 3px 8px;
  border-radius: 12px;
  backdrop-filter: blur(4px);
}

.zen-carousel-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.55);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

.zen-carousel-dot.active {
  width: 18px;
  border-radius: 4px;
  background: #FFFFFF;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.6);
}

/* 诗意微标 (右上角) */
.zen-carousel-badge {
  position: absolute;
  top: 10px;
  right: 12px;
  background: rgba(253, 251, 248, 0.88);
  border: 1px solid rgba(226, 220, 209, 0.85);
  border-radius: 14px;
  padding: 3px 10px;
  font-size: 11.5px;
  color: var(--color-ink);
  font-family: var(--font-serif);
  display: inline-flex;
  align-items: center;
  gap: 5px;
  z-index: 5;
  backdrop-filter: blur(4px);
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(34, 31, 27, 0.06);
  transition: opacity 0.3s ease;
}

.zen-carousel-badge .badge-title {
  font-weight: 700;
  color: var(--color-primary);
}

.zen-carousel-badge .badge-sub {
  color: var(--color-muted);
  font-family: var(--font-sans);
  font-size: 11px;
}

@media (max-width: 600px) {
  .zen-carousel-badge .badge-sub {
    display: none;
  }
  .zen-carousel-badge .badge-divider {
    display: none;
  }
}

/* 兼容老样式名 */
.zen-tea-banner {
  display: none;
}"""

    content = content[:m_css.start()] + new_css + content[m_css.end():]

    # 2. 替换 HTML
    m_html = re.search(r'<div class="zen-tea-banner">\s*<img src="assets/ui/tea_tranquility\.jpg"[^>]*>\s*</div>', content, re.DOTALL)
    if not m_html:
        raise RuntimeError("HTML anchor for banner not found")

    new_html = """<!-- 首页东方心境画卷轮播 Banner (5大意境画卷 · 平滑水墨渐隐) -->
        <div class="zen-carousel-container" id="zenBannerCarousel" aria-label="悟堂东方心境画卷轮播">
          <!-- 幻灯片容器 -->
          <div class="zen-carousel-slides" id="zenCarouselSlides">
            <div class="zen-carousel-slide active" data-idx="0" onclick="drawRandomZen96Card()" title="点击抽取今日觉察灵感/心签">
              <img src="assets/ui/tea_tranquility.jpg" alt="禅茶一味" class="zen-carousel-img">
            </div>
          </div>

          <!-- 诗意意境徽章 -->
          <div class="zen-carousel-badge" id="zenCarouselBadge">
            <span class="badge-title" id="zenCarouselTitle">禅茶一味</span>
            <span class="badge-divider">·</span>
            <span class="badge-sub" id="zenCarouselSubtitle">偷得浮生半日闲 · 煮一盏温热清茶</span>
          </div>

          <!-- 左右翻页轻巧控制箭头 -->
          <button type="button" class="zen-carousel-arrow prev" id="zenCarouselPrev" aria-label="上一幅画卷" title="上一幅画卷">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"></polyline></svg>
          </button>
          <button type="button" class="zen-carousel-arrow next" id="zenCarouselNext" aria-label="下一幅画卷" title="下一幅画卷">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>

          <!-- 底部典籍金分页指示胶囊 -->
          <div class="zen-carousel-dots" id="zenCarouselDots"></div>
        </div>"""

    content = content[:m_html.start()] + new_html + content[m_html.end():]

    # 3. 注入 JS 逻辑
    js_anchor = "function initSchoolTrackSelector() {"
    if js_anchor not in content:
        raise RuntimeError("js_anchor not found")

    carousel_js = """// ==========================================================================
  // 首页东方心境画卷轮播引擎 (Zen Banner Carousel)
  // ==========================================================================
  var ZEN_BANNER_ITEMS = [
    {
      id: 'tea',
      src: 'assets/ui/tea_tranquility.jpg',
      title: '禅茶一味',
      subtitle: '偷得浮生半日闲 · 煮一盏温热清茶',
      tip: '点击抽取今日觉察灵感/心签'
    },
    {
      id: 'bamboo',
      src: 'assets/ui/bamboo_breeze.jpg',
      title: '修竹清风',
      subtitle: '虚心有节明心志 · 任尔东西南北风',
      tip: '点击抽取今日觉察灵感/心签'
    },
    {
      id: 'stones',
      src: 'assets/ui/zen_stones_banner.jpg',
      title: '枯山静水',
      subtitle: '止水澄镜鉴尘心 · 静观万物皆自得',
      tip: '点击抽取今日觉察灵感/心签'
    },
    {
      id: 'pine',
      src: 'assets/ui/pine_mountain.jpg',
      title: '松风远岫',
      subtitle: '苍松破雾立风骨 · 澄怀观道见青山',
      tip: '点击抽取今日觉察灵感/心签'
    },
    {
      id: 'lotus',
      src: 'assets/ui/lotus_pond.jpg',
      title: '碧潭青莲',
      subtitle: '出水自洁不染尘 · 抚平千丝繁杂念',
      tip: '点击抽取今日觉察灵感/心签'
    }
  ];

  var currentBannerIndex = 0;
  var bannerAutoplayTimer = null;

  function initZenBannerCarousel() {
    var container = $('zenBannerCarousel');
    var slidesWrap = $('zenCarouselSlides');
    var dotsWrap = $('zenCarouselDots');
    if (!container || !slidesWrap) return;

    // 渲染幻灯片列表
    slidesWrap.innerHTML = ZEN_BANNER_ITEMS.map(function(item, idx) {
      var activeCls = (idx === 0) ? ' active' : '';
      return '<div class="zen-carousel-slide' + activeCls + '" data-idx="' + idx + '" onclick="drawRandomZen96Card()" title="' + esc(item.tip) + '">' +
        '<img src="' + esc(item.src) + '" alt="' + esc(item.title) + '" class="zen-carousel-img">' +
      '</div>';
    }).join('');

    // 渲染分页指示胶囊
    if (dotsWrap) {
      dotsWrap.innerHTML = ZEN_BANNER_ITEMS.map(function(item, idx) {
        var activeCls = (idx === 0) ? ' active' : '';
        return '<div class="zen-carousel-dot' + activeCls + '" data-idx="' + idx + '" title="' + esc(item.title) + '"></div>';
      }).join('');

      dotsWrap.onclick = function(e) {
        var dot = e.target.closest('.zen-carousel-dot');
        if (!dot) return;
        var idx = parseInt(dot.getAttribute('data-idx'), 10);
        goToZenBanner(idx);
      };
    }

    // 左右按钮事件
    var prevBtn = $('zenCarouselPrev');
    var nextBtn = $('zenCarouselNext');
    if (prevBtn) {
      prevBtn.onclick = function(e) {
        e.stopPropagation();
        goToZenBanner((currentBannerIndex - 1 + ZEN_BANNER_ITEMS.length) % ZEN_BANNER_ITEMS.length);
      };
    }
    if (nextBtn) {
      nextBtn.onclick = function(e) {
        e.stopPropagation();
        goToZenBanner((currentBannerIndex + 1) % ZEN_BANNER_ITEMS.length);
      };
    }

    // 悬停暂停自动轮播
    container.onmouseenter = function() { stopBannerAutoplay(); };
    container.onmouseleave = function() { startBannerAutoplay(); };

    // 移动端手势轻扫滑动支持
    var touchStartX = 0;
    container.addEventListener('touchstart', function(e) {
      if (e.touches && e.touches[0]) {
        touchStartX = e.touches[0].clientX;
        stopBannerAutoplay();
      }
    }, { passive: true });

    container.addEventListener('touchend', function(e) {
      if (e.changedTouches && e.changedTouches[0]) {
        var touchEndX = e.changedTouches[0].clientX;
        var diff = touchStartX - touchEndX;
        if (Math.abs(diff) > 36) {
          if (diff > 0) {
            goToZenBanner((currentBannerIndex + 1) % ZEN_BANNER_ITEMS.length);
          } else {
            goToZenBanner((currentBannerIndex - 1 + ZEN_BANNER_ITEMS.length) % ZEN_BANNER_ITEMS.length);
          }
        }
        startBannerAutoplay();
      }
    }, { passive: true });

    updateZenBannerBadge(0);
    startBannerAutoplay();
  }

  function goToZenBanner(idx) {
    if (idx === currentBannerIndex) return;
    var slides = document.querySelectorAll('#zenCarouselSlides .zen-carousel-slide');
    var dots = document.querySelectorAll('#zenCarouselDots .zen-carousel-dot');

    if (slides[currentBannerIndex]) slides[currentBannerIndex].classList.remove('active');
    if (dots[currentBannerIndex]) dots[currentBannerIndex].classList.remove('active');

    currentBannerIndex = idx;

    if (slides[currentBannerIndex]) slides[currentBannerIndex].classList.add('active');
    if (dots[currentBannerIndex]) dots[currentBannerIndex].classList.add('active');

    updateZenBannerBadge(currentBannerIndex);
  }

  function updateZenBannerBadge(idx) {
    var item = ZEN_BANNER_ITEMS[idx];
    if (!item) return;
    var titleEl = $('zenCarouselTitle');
    var subEl = $('zenCarouselSubtitle');
    if (titleEl) titleEl.textContent = item.title;
    if (subEl) subEl.textContent = item.subtitle;
  }

  function startBannerAutoplay() {
    stopBannerAutoplay();
    bannerAutoplayTimer = setInterval(function() {
      goToZenBanner((currentBannerIndex + 1) % ZEN_BANNER_ITEMS.length);
    }, 4500);
  }

  function stopBannerAutoplay() {
    if (bannerAutoplayTimer) {
      clearInterval(bannerAutoplayTimer);
      bannerAutoplayTimer = null;
    }
  }

  """ + js_anchor

    content = content.replace(js_anchor, carousel_js, 1)

    # 4. 在初始化入口处调用 initZenBannerCarousel
    m_init_call = "initSchoolTrackSelector();"
    if m_init_call not in content:
        raise RuntimeError("init_call anchor not found")

    new_init_call = "initSchoolTrackSelector();\n      initZenBannerCarousel();"
    content = content.replace(m_init_call, new_init_call, 1)

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("[ok] Banner carousel patched successfully into _template.html!")

if __name__ == "__main__":
    main()
