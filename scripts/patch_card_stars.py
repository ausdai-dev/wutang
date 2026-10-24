# -*- coding: utf-8 -*-
"""
为悟堂卡牌（今日觉察牌、心境牌、智慧牌、行动牌）注入神秘深空星云与星空粒子动画背景。
包含：
1. 呼吸旋转的多彩深空星云 (Breathing Mystic Nebula)
2. 漫天星尘与闪烁繁星 (Twinkling Starlight Particles)
3. 随机划过天际的流星 (Shooting Meteors)
4. 优雅耀目的十字星芒 (Diamond Star Glints)
5. 缓缓上升的东方流金微尘 (Floating Golden Embers)
6. 天体星轨罗盘升级（自转卫星节点与中心朱砂印神光）
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "frontend" / "_template.html"

NEW_CSS = """/* ========================================================
   卡背：神秘深空天体罗盘与星空粒子动画 (Cosmic Nebula & Starry Particles)
   ======================================================== */

.card-3d-back,
.awareness-card-back.card-3d-back {
  position: absolute;
  inset: 0;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 16px;
  overflow: hidden;
  background: radial-gradient(ellipse at 50% 28%, #1c1145 0%, #0e082b 45%, #050212 100%) !important;
  border: 1px solid rgba(245, 197, 66, 0.45) !important;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 16px 14px;
  color: #eeddbb;
  box-sizing: border-box;
  box-shadow: inset 0 0 35px rgba(5, 2, 18, 0.9), 0 14px 38px rgba(5, 3, 18, 0.45);
}

/* 1. 动态流动星云 (Breathing Mystic Nebula) */
.card-3d-back::before {
  content: "";
  position: absolute;
  inset: -25%;
  width: 150%;
  height: 150%;
  background: 
    radial-gradient(circle at 45% 30%, rgba(139, 92, 246, 0.25) 0%, transparent 48%),
    radial-gradient(circle at 75% 68%, rgba(217, 119, 6, 0.18) 0%, transparent 42%),
    radial-gradient(circle at 25% 72%, rgba(14, 165, 233, 0.16) 0%, transparent 46%),
    radial-gradient(circle at 50% 50%, rgba(245, 158, 11, 0.22) 0%, transparent 62%);
  filter: blur(20px);
  opacity: 0.85;
  animation: cosmicNebulaShift 18s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: 1;
}

/* 2. 漫天星尘与闪烁繁星 (Twinkling Star Dust Field) */
.card-3d-back::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(1px 1px at 20px 30px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1.2px 1.2px at 45px 75px, rgba(245, 197, 66, 0.85), transparent),
    radial-gradient(1.5px 1.5px at 60px 160px, rgba(255, 255, 255, 0.95), transparent),
    radial-gradient(1px 1px at 95px 45px, rgba(147, 197, 253, 0.8), transparent),
    radial-gradient(1.8px 1.8px at 135px 85px, rgba(255, 255, 255, 0.98), transparent),
    radial-gradient(1px 1px at 170px 125px, rgba(253, 224, 71, 0.8), transparent),
    radial-gradient(1.2px 1.2px at 215px 48px, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(1.6px 1.6px at 245px 100px, rgba(245, 197, 66, 0.95), transparent),
    radial-gradient(1px 1px at 275px 145px, rgba(255, 255, 255, 0.75), transparent),
    radial-gradient(1.3px 1.3px at 32px 225px, rgba(196, 181, 253, 0.85), transparent),
    radial-gradient(1px 1px at 75px 285px, rgba(255, 255, 255, 0.75), transparent),
    radial-gradient(1.5px 1.5px at 115px 245px, rgba(245, 197, 66, 0.9), transparent),
    radial-gradient(1px 1px at 155px 315px, rgba(255, 255, 255, 0.9), transparent),
    radial-gradient(1.4px 1.4px at 205px 275px, rgba(147, 197, 253, 0.85), transparent),
    radial-gradient(1px 1px at 255px 335px, rgba(255, 255, 255, 0.8), transparent),
    radial-gradient(1.7px 1.7px at 285px 265px, rgba(253, 224, 71, 0.95), transparent),
    radial-gradient(1px 1px at 48px 385px, rgba(255, 255, 255, 0.85), transparent),
    radial-gradient(1.3px 1.3px at 90px 425px, rgba(245, 197, 66, 0.8), transparent),
    radial-gradient(1px 1px at 145px 395px, rgba(196, 181, 253, 0.8), transparent),
    radial-gradient(1.6px 1.6px at 195px 445px, rgba(255, 255, 255, 0.98), transparent),
    radial-gradient(1px 1px at 240px 405px, rgba(245, 197, 66, 0.85), transparent),
    radial-gradient(1.3px 1.3px at 280px 455px, rgba(255, 255, 255, 0.8), transparent);
  background-size: 310px 480px;
  opacity: 0.85;
  animation: starsTwinklePulse 6s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: 1;
}

/* 3. 独立星空粒子动态层 (Star Particles Layer) */
.card-stars-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
  overflow: hidden;
  border-radius: 16px;
}

/* 十字星芒 (Glittering Star Glints) */
.star-glint {
  position: absolute;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 0 6px 1.5px rgba(254, 240, 138, 0.95), 0 0 12px 2px rgba(245, 197, 66, 0.6);
  pointer-events: none;
}
.star-glint::before, .star-glint::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: linear-gradient(to right, transparent, rgba(254, 240, 138, 0.95), transparent);
}
.star-glint::before { width: 14px; height: 1px; }
.star-glint::after { width: 1px; height: 14px; }

.star-glint.g1 { top: 16%; left: 20%; animation: glintBlink 4.2s ease-in-out infinite; }
.star-glint.g2 { top: 24%; right: 18%; animation: glintBlink 5.6s ease-in-out 1.3s infinite; }
.star-glint.g3 { bottom: 22%; left: 16%; animation: glintBlink 4.8s ease-in-out 2.2s infinite; }
.star-glint.g4 { bottom: 18%; right: 22%; animation: glintBlink 6.2s ease-in-out 0.7s infinite; }

/* 划过星空的流星 (Shooting Stars) */
.card-meteor {
  position: absolute;
  top: 10%;
  left: -50px;
  width: 80px;
  height: 1.5px;
  background: linear-gradient(90deg, transparent, rgba(254, 240, 138, 0.85) 65%, #FFFFFF 100%);
  transform: rotate(-35deg);
  border-radius: 50%;
  filter: drop-shadow(0 0 5px rgba(254, 240, 138, 0.95));
  opacity: 0;
  animation: meteorShower 8.5s cubic-bezier(0.2, 0.7, 0.3, 1) infinite;
  pointer-events: none;
}
.card-meteor.m2 {
  top: 55%;
  left: -40px;
  width: 60px;
  height: 1.2px;
  animation-delay: 4.8s;
  animation-duration: 9.5s;
}

/* 浮动金色微尘粒子 (Floating Stardust Particles) */
.card-particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(253, 230, 138, 0.85);
  box-shadow: 0 0 6px rgba(245, 197, 66, 0.8);
  pointer-events: none;
}
.card-particle.p1 { left: 18%; width: 2.5px; height: 2.5px; animation: particleFloat 7s ease-in-out infinite; }
.card-particle.p2 { left: 42%; width: 2px; height: 2px; animation: particleFloat 9s ease-in-out 1.8s infinite; }
.card-particle.p3 { left: 68%; width: 3px; height: 3px; animation: particleFloat 8s ease-in-out 3.2s infinite; }
.card-particle.p4 { left: 28%; width: 1.8px; height: 1.8px; animation: particleFloat 10s ease-in-out 4.5s infinite; }
.card-particle.p5 { left: 82%; width: 2.5px; height: 2.5px; animation: particleFloat 8.5s ease-in-out 2.4s infinite; }

/* 4. 边角纹样与金色边线 */
.card-corner {
  position: absolute;
  width: 12px;
  height: 12px;
  border-color: rgba(245, 197, 66, 0.85);
  filter: drop-shadow(0 0 3px rgba(245, 197, 66, 0.6));
  pointer-events: none;
  z-index: 3;
}

.card-corner.tl { top: 9px; left: 9px; border-top: 1.8px solid; border-left: 1.8px solid; }
.card-corner.tr { top: 9px; right: 9px; border-top: 1.8px solid; border-right: 1.8px solid; }
.card-corner.bl { bottom: 9px; left: 9px; border-bottom: 1.8px solid; border-left: 1.8px solid; }
.card-corner.br { bottom: 9px; right: 9px; border-bottom: 1.8px solid; border-right: 1.8px solid; }

.card-back-header {
  font-family: monospace;
  font-size: 9px;
  letter-spacing: 0.35em;
  color: rgba(253, 230, 138, 0.9);
  text-shadow: 0 0 8px rgba(245, 197, 66, 0.5);
  text-transform: uppercase;
  z-index: 3;
  text-align: center;
}

.card-back-center {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 130px;
  z-index: 3;
}

/* 中心天体星芒光晕 (Cosmic Ring Aura) */
.card-back-center::before {
  content: "";
  position: absolute;
  width: 170px;
  height: 170px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(245, 197, 66, 0.22) 0%, rgba(220, 38, 38, 0.1) 45%, transparent 70%);
  filter: blur(10px);
  animation: pulseAura 4.5s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

/* 天体外环带卫星星宿 */
.card-orbit-ring {
  position: absolute;
  width: 110px;
  height: 110px;
  border-radius: 50%;
  border: 1px dashed rgba(245, 197, 66, 0.5);
  box-shadow: 0 0 16px rgba(245, 197, 66, 0.25), inset 0 0 12px rgba(245, 197, 66, 0.15);
  animation: orbitBreath 8s ease-in-out infinite;
  z-index: 1;
}

.card-orbit-ring::after {
  content: "";
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #FFFBEB;
  box-shadow: 0 0 8px 2px rgba(245, 197, 66, 0.95);
}

/* 天体内环反向旋转 */
.card-orbit-ring-inner {
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 1px double rgba(245, 197, 66, 0.5);
  box-shadow: 0 0 10px rgba(245, 197, 66, 0.2);
  animation: spinOrbitRev 22s linear infinite;
  z-index: 1;
}

.card-orbit-ring-inner::after {
  content: "";
  position: absolute;
  bottom: -3px;
  left: 50%;
  transform: translateX(-50%);
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #FDE68A;
  box-shadow: 0 0 6px 1.5px rgba(245, 197, 66, 0.9);
}

/* 印章 · 悟 (立体金边与朱砂神光) */
.card-seal {
  position: relative;
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #a82424 0%, #851c1c 100%);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-serif);
  font-size: 24px;
  font-weight: 700;
  color: #FDF6EC;
  box-shadow: 0 0 16px rgba(186, 44, 44, 0.65), 0 0 28px rgba(245, 197, 66, 0.35);
  z-index: 3;
  animation: sealBreath 5s ease-in-out infinite;
}

.card-seal::before {
  content: '';
  position: absolute;
  inset: 3px;
  border: 1.5px solid rgba(253, 246, 236, 0.55);
  border-radius: 3px;
}

.card-back-footer {
  font-family: var(--font-serif);
  font-size: 10px;
  letter-spacing: 0.25em;
  color: rgba(253, 230, 138, 0.85);
  text-shadow: 0 0 8px rgba(245, 197, 66, 0.4);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  z-index: 3;
  text-align: center;
}

.card-back-footer .tap-hint {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 0.1em;
  animation: pulseAura 2.5s infinite ease-in-out;
}

/* 核心关键帧动画 */
@keyframes cosmicNebulaShift {
  0% { transform: scale(1) rotate(0deg); opacity: 0.75; }
  50% { transform: scale(1.12) rotate(180deg); opacity: 0.95; }
  100% { transform: scale(1) rotate(360deg); opacity: 0.75; }
}

@keyframes starsTwinklePulse {
  0% { opacity: 0.65; transform: scale(0.99); }
  50% { opacity: 0.95; transform: scale(1.01); }
  100% { opacity: 0.75; transform: scale(1); }
}

@keyframes glintBlink {
  0%, 100% { transform: scale(0.65); opacity: 0.3; }
  50% { transform: scale(1.35); opacity: 1; filter: drop-shadow(0 0 6px rgba(254, 240, 138, 0.95)); }
}

@keyframes meteorShower {
  0% { transform: translate(-60px, -40px) rotate(-35deg); opacity: 0; }
  3% { opacity: 0.95; }
  12% { transform: translate(340px, 230px) rotate(-35deg); opacity: 0; }
  100% { transform: translate(340px, 230px) rotate(-35deg); opacity: 0; }
}

@keyframes particleFloat {
  0% { bottom: -10px; opacity: 0; transform: translateX(0); }
  20% { opacity: 0.85; }
  80% { opacity: 0.75; }
  100% { bottom: 105%; opacity: 0; transform: translateX(18px); }
}

@keyframes sealBreath {
  0%, 100% { box-shadow: 0 0 14px rgba(186, 44, 44, 0.6), 0 0 24px rgba(245, 197, 66, 0.25); transform: scale(1); }
  50% { box-shadow: 0 0 22px rgba(186, 44, 44, 0.85), 0 0 36px rgba(245, 197, 66, 0.45); transform: scale(1.03); }
}

"""

STARS_LAYER_SNIPPET = (
    '<div class="card-stars-layer" aria-hidden="true">'
    '<div class="card-meteor"></div><div class="card-meteor m2"></div>'
    '<div class="star-glint g1"></div><div class="star-glint g2"></div>'
    '<div class="star-glint g3"></div><div class="star-glint g4"></div>'
    '<div class="card-particle p1"></div><div class="card-particle p2"></div>'
    '<div class="card-particle p3"></div><div class="card-particle p4"></div>'
    '<div class="card-particle p5"></div>'
    '</div>'
)


def patch():
    content = TEMPLATE_PATH.read_text(encoding="utf-8")

    # 1. 替换 CSS
    css_start = content.find("/* 卡背：神秘深空与金色天体罗盘")
    css_end = content.find("@keyframes orbitBreath {")
    if css_start == -1 or css_end == -1:
        print("[!] 无法定位 CSS 区域")
        return False

    content = content[:css_start] + NEW_CSS + content[css_end:]

    # 2. 注入今日觉察牌 HTML
    target_awareness = '<div class="awareness-card-face awareness-card-back card-3d-back">'
    if target_awareness in content and 'class="card-stars-layer"' not in content[content.find(target_awareness):content.find(target_awareness)+500]:
        replacement = target_awareness + '\n                  ' + STARS_LAYER_SNIPPET
        content = content.replace(target_awareness, replacement, 1)
        print("[ok] 今日觉察牌卡背已注入星空粒子层")

    # 3. 注入三步解忧卡牌组 JS
    js_marker = "var a = cards.action;"
    if js_marker in content and "var STARS_LAYER_HTML =" not in content:
        js_inject = (
            "var a = cards.action;\n"
            f"    var STARS_LAYER_HTML = '{STARS_LAYER_SNIPPET}';"
        )
        content = content.replace(js_marker, js_inject, 1)

        # 在三张牌的 card-3d-back 后面拼接 STARS_LAYER_HTML
        content = content.replace(
            "  <div class=\"card-3d-face card-3d-back\">'\n\n      + '    <div class=\"card-corner tl\">",
            "  <div class=\"card-3d-face card-3d-back\">' + STARS_LAYER_HTML\n\n      + '    <div class=\"card-corner tl\">"
        )
        print("[ok] 三步解忧牌（心境/智慧/行动）已注入星空粒子层")

    TEMPLATE_PATH.write_text(content, encoding="utf-8")
    print("[ok] _template.html 更新完成！")
    return True


if __name__ == "__main__":
    if patch():
        import subprocess
        subprocess.run(["python", str(ROOT / "scripts" / "build_frontend.py")], check=True)
