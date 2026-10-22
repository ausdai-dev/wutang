# -*- coding: utf-8 -*-
"""
OH-Card Style Procedural Watercolor Illustration Generator
Generates atmospheric, dreamy, wet-on-wet metaphorical watercolor illustrations
with realistic paper textures, pigment granulation, and psychological projective motifs.
"""

import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT, "frontend", "assets", "cards", "mindset")
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 896, 1200

def create_noise_layer(width, height, scale=32, octaves=4):
    """Generate fractal coherent noise for watercolor wetness."""
    grid = np.zeros((height, width), dtype=np.float32)
    freq = scale
    amp = 1.0
    for _ in range(octaves):
        low_w = max(2, int(width / freq))
        low_h = max(2, int(height / freq))
        r = np.random.rand(low_h, low_w).astype(np.float32)
        r_img = Image.fromarray((r * 255).astype(np.uint8)).resize((width, height), Image.Resampling.BILINEAR)
        grid += (np.array(r_img, dtype=np.float32) / 255.0) * amp
        freq *= 0.5
        amp *= 0.5
    grid = (grid - grid.min()) / (grid.max() - grid.min() + 1e-6)
    return grid

def create_paper_texture(width, height):
    """Generate cold-press watercolor paper grain."""
    base = Image.new("RGB", (width, height), (252, 249, 243))
    grain = np.random.normal(128, 7, (height, width)).clip(0, 255).astype(np.uint8)
    g_img = Image.fromarray(grain, mode="L").filter(ImageFilter.GaussianBlur(0.6))
    noise = (create_noise_layer(width, height, scale=48, octaves=3) * 16).astype(np.uint8)
    n_img = Image.fromarray(noise, mode="L")
    
    paper = Image.blend(base, Image.new("RGB", (width, height), (245, 240, 230)), 0.35)
    paper = ImageChops.multiply(paper, g_img.convert("RGB"))
    return paper

def apply_watercolor_wash(base_img, mask_arr, color_rgb, opacity=0.7, edge_darkening=True, blur_radius=18):
    """Apply a wet-on-wet watercolor layer with organic granulation and drying edge."""
    noise = create_noise_layer(W, H, scale=28, octaves=3)
    perturbed_mask = mask_arr * (0.82 + 0.36 * noise)
    perturbed_mask = np.clip(perturbed_mask, 0.0, 1.0)
    
    m_img = Image.fromarray((perturbed_mask * 255).astype(np.uint8), mode="L")
    m_blurred = m_img.filter(ImageFilter.GaussianBlur(blur_radius))
    
    if edge_darkening:
        edge = ImageChops.difference(m_blurred.filter(ImageFilter.MaxFilter(7)), m_blurred.filter(ImageFilter.MinFilter(3)))
        edge_arr = np.array(edge, dtype=np.float32) / 255.0
        final_alpha = np.clip(np.array(m_blurred, dtype=np.float32)/255.0 + edge_arr * 0.4, 0.0, 1.0)
    else:
        final_alpha = np.array(m_blurred, dtype=np.float32) / 255.0
        
    final_alpha = final_alpha * opacity
    
    color_layer = Image.new("RGB", (W, H), color_rgb)
    wash_rgba = Image.new("RGBA", (W, H))
    wash_rgba.paste(color_layer, (0, 0), Image.fromarray((final_alpha * 255).astype(np.uint8), mode="L"))
    
    base_rgba = base_img.convert("RGBA")
    combined = Image.alpha_composite(base_rgba, wash_rgba)
    return combined.convert("RGB")

def add_paper_vignette(img):
    """Soft border vignette simulating vintage watercolor paper deckled edges."""
    vignette = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(vignette)
    draw.rectangle([40, 40, W - 40, H - 40], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(32))
    
    border_col = Image.new("RGB", (W, H), (242, 236, 224))
    res = Image.composite(img, border_col, vignette)
    return res

# --------------------------------------------------------------------------
# Card Specific Painters
# --------------------------------------------------------------------------

def render_m003_fear_starting():
    """M-003: 不敢开始 (A glowing doorway in morning mist, dawn light spilling)"""
    img = create_paper_texture(W, H)
    
    # 1. Background sky wash (lavender into warm peach)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    sky_mask = np.clip((H*0.75 - y_coords) / (H*0.6), 0, 1)
    img = apply_watercolor_wash(img, sky_mask, (155, 150, 182), opacity=0.45) # Soft lavender
    
    peach_mask = np.clip((H*0.85 - y_coords) / (H*0.5) * (x_coords / W), 0, 1)
    img = apply_watercolor_wash(img, peach_mask, (228, 175, 142), opacity=0.5) # Warm peach
    
    # 2. Ground wash (misty damp stones)
    ground_mask = np.clip((y_coords - H*0.55) / (H*0.45), 0, 1)
    img = apply_watercolor_wash(img, ground_mask, (142, 148, 140), opacity=0.55) # Misty slate green
    
    # 3. Floating wooden doorway in center
    door_mask = np.zeros((H, W), dtype=np.float32)
    door_mask[int(H*0.28):int(H*0.68), int(W*0.35):int(W*0.65)] = 1.0
    # carve out inner light
    inner_light = np.zeros((H, W), dtype=np.float32)
    inner_light[int(H*0.30):int(H*0.68), int(W*0.37):int(W*0.63)] = 1.0
    door_frame = door_mask - inner_light
    
    img = apply_watercolor_wash(img, door_frame, (96, 75, 62), opacity=0.75, blur_radius=6) # Wood frame
    img = apply_watercolor_wash(img, inner_light, (255, 235, 170), opacity=0.85, blur_radius=15) # Radiant dawn light
    
    # 4. Spilling light onto path
    spill_mask = np.zeros((H, W), dtype=np.float32)
    for y in range(int(H*0.65), H):
        factor = (y - H*0.65) / (H*0.35)
        x_min = int(W*0.35 - factor * W*0.22)
        x_max = int(W*0.65 + factor * W*0.22)
        spill_mask[y, max(0, x_min):min(W, x_max)] = (1.0 - factor*0.3)
    img = apply_watercolor_wash(img, spill_mask, (250, 220, 150), opacity=0.55, blur_radius=24)
    
    # 5. Hesitating footprint silhouette at threshold
    step_mask = np.zeros((H, W), dtype=np.float32)
    step_mask[int(H*0.67):int(H*0.70), int(W*0.46):int(W*0.54)] = 1.0
    img = apply_watercolor_wash(img, step_mask, (80, 70, 75), opacity=0.6, blur_radius=5)
    
    return add_paper_vignette(img)


def render_m004_exhausted():
    """M-004: 已经很累了 (Resting curled form nestled in hollow of moss, gentle rain)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Deep indigo rain cloud wash above
    rain_mask = np.clip((H*0.55 - y_coords) / (H*0.5), 0, 1)
    img = apply_watercolor_wash(img, rain_mask, (95, 115, 150), opacity=0.6)
    img = apply_watercolor_wash(img, rain_mask * 0.7, (65, 80, 115), opacity=0.45, blur_radius=22)
    
    # 2. Gentle downward rainfall streaks
    streaks = (create_noise_layer(W, H, scale=12, octaves=2) > 0.65).astype(np.float32)
    streaks *= np.clip((H*0.7 - y_coords) / (H*0.5), 0, 1)
    img = apply_watercolor_wash(img, streaks, (140, 160, 190), opacity=0.35, blur_radius=8)
    
    # 3. Soft mossy earth hollow below
    earth_mask = np.clip((y_coords - H*0.48) / (H*0.4), 0, 1)
    img = apply_watercolor_wash(img, earth_mask, (110, 135, 105), opacity=0.65) # Muted sage
    img = apply_watercolor_wash(img, earth_mask * 0.8, (80, 100, 75), opacity=0.45) # Deep moss
    
    # 4. Curled resting figure / leaf in the center hollow
    nest_mask = np.zeros((H, W), dtype=np.float32)
    cx, cy = int(W*0.5), int(H*0.62)
    rx, ry = int(W*0.22), int(H*0.14)
    dist = ((x_coords - cx) / rx)**2 + ((y_coords - cy) / ry)**2
    nest_mask = np.clip(1.0 - dist, 0, 1)
    img = apply_watercolor_wash(img, nest_mask, (215, 185, 145), opacity=0.65, blur_radius=12) # Warm resting cocoon
    img = apply_watercolor_wash(img, nest_mask * 0.6, (170, 140, 110), opacity=0.5, blur_radius=8)
    
    return add_paper_vignette(img)


def render_m005_self_blame():
    """M-005: 为什么总是我的错 (Gentle palms holding a pebble, towering misty mountain)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Warm neutral sky
    sky = np.clip((H*0.6 - y_coords) / (H*0.5), 0, 1)
    img = apply_watercolor_wash(img, sky, (185, 180, 175), opacity=0.4)
    
    # 2. Towering misty mountain looming in background
    mountain_mask = np.zeros((H, W), dtype=np.float32)
    for x in range(W):
        peak_y = int(H*0.15 + abs(x - W*0.5) * 0.9)
        if peak_y < H:
            mountain_mask[peak_y:int(H*0.75), x] = 1.0
    img = apply_watercolor_wash(img, mountain_mask, (100, 95, 105), opacity=0.4, blur_radius=20) # Misty giant
    
    # 3. Two cupped hands in foreground
    hands_mask = np.zeros((H, W), dtype=np.float32)
    cx, cy = int(W*0.5), int(H*0.72)
    rx, ry = int(W*0.28), int(H*0.16)
    dist = ((x_coords - cx) / rx)**2 + ((y_coords - cy) / ry)**2
    hands_mask = np.clip(1.0 - dist, 0, 1)
    img = apply_watercolor_wash(img, hands_mask, (210, 175, 150), opacity=0.65, blur_radius=16) # Cupped hands
    
    # 4. Small smooth stone resting in the center
    stone_mask = np.zeros((H, W), dtype=np.float32)
    scx, scy = int(W*0.5), int(H*0.69)
    srx, sry = int(W*0.09), int(H*0.06)
    sdist = ((x_coords - scx) / srx)**2 + ((y_coords - scy) / sry)**2
    stone_mask = np.clip(1.0 - sdist, 0, 1)
    img = apply_watercolor_wash(img, stone_mask, (70, 70, 75), opacity=0.8, blur_radius=5)
    
    return add_paper_vignette(img)


def render_m006_fear_rejection():
    """M-006: 害怕被拒绝 (Translucent umbrella, circular ripples safe haven)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Rainy lavender-jade backdrop
    img = apply_watercolor_wash(img, np.ones((H, W), dtype=np.float32), (160, 175, 185), opacity=0.35)
    
    # 2. Paper umbrella dome
    cx, cy = int(W*0.5), int(H*0.42)
    rx, ry = int(W*0.34), int(H*0.22)
    umbrella_mask = np.zeros((H, W), dtype=np.float32)
    dist = ((x_coords - cx) / rx)**2 + ((y_coords - cy) / ry)**2
    umbrella_mask = (dist <= 1.0) & (y_coords <= cy)
    img = apply_watercolor_wash(img, umbrella_mask.astype(np.float32), (235, 185, 170), opacity=0.55, blur_radius=10) # Translucent coral
    
    # Umbrella ribs
    ribs = np.zeros((H, W), dtype=np.float32)
    for angle in np.linspace(-math.pi*0.8, -math.pi*0.2, 7):
        for r in range(0, int(rx*0.95)):
            px = int(cx + r * math.cos(angle))
            py = int(cy + r * math.sin(angle) * (ry/rx))
            if 0 <= px < W and 0 <= py < H:
                ribs[py, px] = 1.0
    img = apply_watercolor_wash(img, ribs, (140, 95, 85), opacity=0.5, blur_radius=3)
    
    # 3. Soft glowing safe space beneath
    under_mask = np.zeros((H, W), dtype=np.float32)
    dist_under = ((x_coords - cx) / (rx*0.85))**2 + ((y_coords - (cy+H*0.2)) / (H*0.25))**2
    under_mask = np.clip(1.0 - dist_under, 0, 1)
    img = apply_watercolor_wash(img, under_mask, (255, 240, 200), opacity=0.5, blur_radius=20)
    
    # 4. Circular ripple boundaries on ground
    ripples = np.zeros((H, W), dtype=np.float32)
    for rad in [140, 200, 260]:
        rcx, rcy = int(W*0.5), int(H*0.8)
        rdist = np.sqrt(((x_coords - rcx))**2 + ((y_coords - rcy)*2.2)**2)
        ripples += np.clip(1.0 - np.abs(rdist - rad)/14.0, 0, 1)
    img = apply_watercolor_wash(img, ripples, (120, 155, 170), opacity=0.5, blur_radius=5)
    
    return add_paper_vignette(img)


def render_m008_peer_pressure():
    """M-008: 同辈追赶焦虑 (Diverging paths, floating wildflowers, own tempo)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Rolling hill washes in sage, ochre and misty blue
    hill1 = np.clip((y_coords - (H*0.4 + np.sin(x_coords/W * math.pi * 3)*60)) / 100, 0, 1)
    hill2 = np.clip((y_coords - (H*0.6 + np.cos(x_coords/W * math.pi * 2)*80)) / 120, 0, 1)
    img = apply_watercolor_wash(img, hill1, (165, 180, 160), opacity=0.45)
    img = apply_watercolor_wash(img, hill2, (185, 165, 135), opacity=0.5)
    
    # 2. Three winding diverging paths
    for path_x, col in [(0.25, (215, 150, 140)), (0.5, (140, 170, 195)), (0.75, (220, 195, 120))]:
        path_mask = np.zeros((H, W), dtype=np.float32)
        for y in range(int(H*0.35), H):
            prog = (y - H*0.35) / (H*0.65)
            curr_x = int(W*0.5 + (path_x - 0.5)*W * (prog**1.3) + math.sin(prog * 6) * 35)
            if 0 <= curr_x < W:
                path_mask[y, max(0, curr_x-18):min(W, curr_x+18)] = 1.0
        img = apply_watercolor_wash(img, path_mask, col, opacity=0.6, blur_radius=8)
        
        # Floating wildflower at each path end
        fx = int(W*0.5 + (path_x - 0.5)*W + math.sin(6) * 35)
        fy = int(H*0.88)
        flower_mask = np.zeros((H, W), dtype=np.float32)
        fdist = ((x_coords - fx)/35)**2 + ((y_coords - fy)/35)**2
        flower_mask = np.clip(1.0 - fdist, 0, 1)
        img = apply_watercolor_wash(img, flower_mask, col, opacity=0.8, blur_radius=6)
        
    return add_paper_vignette(img)


def render_m009_imposter_syndrome():
    """M-009: 不配得感 (Small tender bird before glowing golden persimmon on autumn branch)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Warm amber & burnt peach autumn mist
    sky = np.clip(1.0 - (y_coords / H), 0, 1)
    img = apply_watercolor_wash(img, sky, (245, 225, 195), opacity=0.45)
    img = apply_watercolor_wash(img, create_noise_layer(W, H, 36, 3), (230, 180, 140), opacity=0.35)
    
    # 2. Slender ink-watercolor autumn branch
    branch_mask = np.zeros((H, W), dtype=np.float32)
    for x in range(int(W*0.1), int(W*0.85)):
        by = int(H*0.38 + math.sin(x / 90.0) * 30 + (x - W*0.5)*0.2)
        branch_mask[max(0, by-8):min(H, by+8), x] = 1.0
    img = apply_watercolor_wash(img, branch_mask, (85, 70, 60), opacity=0.75, blur_radius=5)
    
    # 3. Glowing golden persimmon fruit hanging down
    fx, fy = int(W*0.62), int(H*0.46)
    fdist = ((x_coords - fx)/50)**2 + ((y_coords - fy)/55)**2
    fruit_mask = np.clip(1.0 - fdist, 0, 1)
    img = apply_watercolor_wash(img, fruit_mask, (240, 130, 45), opacity=0.85, blur_radius=10) # Burnt orange
    img = apply_watercolor_wash(img, fruit_mask * 0.7, (255, 215, 80), opacity=0.9, blur_radius=6) # Golden center
    
    # 4. Small tender bird perched quietly, looking at fruit
    bx, by = int(W*0.38), int(H*0.34)
    bdist = ((x_coords - bx)/40)**2 + ((y_coords - by)/30)**2
    bird_mask = np.clip(1.0 - bdist, 0, 1)
    img = apply_watercolor_wash(img, bird_mask, (110, 120, 135), opacity=0.7, blur_radius=6) # Soft blue-grey bird
    
    return add_paper_vignette(img)


def render_m010_ungrounded():
    """M-010: 悬在半空的心 (Paper kite in rose-lavender twilight clouds, silk ribbon towards earth)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Twilight sky: dusty rose blending to soft lavender
    rose_mask = np.clip((H*0.65 - y_coords) / (H*0.5), 0, 1)
    img = apply_watercolor_wash(img, rose_mask, (215, 160, 170), opacity=0.5)
    lav_mask = np.clip((H*0.45 - y_coords) / (H*0.4), 0, 1)
    img = apply_watercolor_wash(img, lav_mask, (145, 140, 175), opacity=0.45)
    
    # 2. Rich mossy damp ground at the very bottom
    earth = np.clip((y_coords - H*0.8) / (H*0.2), 0, 1)
    img = apply_watercolor_wash(img, earth, (85, 110, 85), opacity=0.65)
    
    # 3. Soft diamond paper kite floating in upper sky
    kx, ky = int(W*0.5), int(H*0.28)
    kite_mask = np.zeros((H, W), dtype=np.float32)
    k_dist = (np.abs(x_coords - kx)/75.0 + np.abs(y_coords - ky)/100.0)
    kite_mask = np.clip(1.0 - k_dist, 0, 1)
    img = apply_watercolor_wash(img, kite_mask, (245, 230, 210), opacity=0.85, blur_radius=6) # Pale kite
    img = apply_watercolor_wash(img, kite_mask * 0.7, (230, 140, 130), opacity=0.6, blur_radius=8)
    
    # 4. Long trailing silk ribbon softly reaching downward
    ribbon_mask = np.zeros((H, W), dtype=np.float32)
    for y in range(int(H*0.35), int(H*0.85)):
        prog = (y - H*0.35) / (H*0.5)
        rx = int(kx + math.sin(prog * 7) * 45 * prog)
        ribbon_mask[y, max(0, rx-5):min(W, rx+5)] = 1.0
    img = apply_watercolor_wash(img, ribbon_mask, (200, 100, 110), opacity=0.55, blur_radius=5)
    
    return add_paper_vignette(img)


def render_m011_judged_by_others():
    """M-011: 被评价绑架 (Silhouette seated cross-legged by mountain lake with shifting ripples)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Distant misty mountains in indigo
    mtn = np.zeros((H, W), dtype=np.float32)
    for x in range(W):
        my = int(H*0.32 + math.sin(x/70.0)*40 + math.cos(x/150.0)*60)
        mtn[my:int(H*0.55), x] = 1.0
    img = apply_watercolor_wash(img, mtn, (95, 105, 135), opacity=0.45, blur_radius=18)
    
    # 2. Lake surface reflecting clouds
    lake = np.clip((y_coords - H*0.5) / (H*0.5), 0, 1)
    img = apply_watercolor_wash(img, lake, (130, 155, 170), opacity=0.55)
    
    # Shifting water ripples of outside gazes
    ripples = (np.sin(y_coords * 0.15) > 0.5).astype(np.float32) * lake
    img = apply_watercolor_wash(img, ripples, (180, 205, 215), opacity=0.3, blur_radius=4)
    
    # 3. Centered, calm seated silhouette
    sx, sy = int(W*0.5), int(H*0.62)
    sdist = ((x_coords - sx)/65)**2 + ((y_coords - sy)/85)**2
    sil_mask = np.clip(1.0 - sdist, 0, 1)
    # Head
    hdist = ((x_coords - sx)/30)**2 + ((y_coords - (sy-65))/30)**2
    sil_mask = np.maximum(sil_mask, np.clip(1.0 - hdist, 0, 1))
    
    img = apply_watercolor_wash(img, sil_mask, (55, 60, 75), opacity=0.8, blur_radius=8)
    
    return add_paper_vignette(img)


def render_m012_pretending_stable():
    """M-012: 假装情绪稳定 (Calm pale surface, secret underwater swirling passions)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Top half: Extremely calm, pristine pale cream & soft mist
    top_mask = np.clip((H*0.48 - y_coords) / (H*0.4), 0, 1)
    img = apply_watercolor_wash(img, top_mask, (245, 240, 230), opacity=0.7)
    
    # Smooth horizontal dividing waterline
    line_mask = np.clip(1.0 - np.abs(y_coords - H*0.48)/10.0, 0, 1)
    img = apply_watercolor_wash(img, line_mask, (160, 180, 190), opacity=0.5, blur_radius=4)
    
    # 2. Bottom half: Deep underwater vortex of hidden swirling emotions
    deep_mask = np.clip((y_coords - H*0.48) / (H*0.5), 0, 1)
    img = apply_watercolor_wash(img, deep_mask, (50, 75, 115), opacity=0.65) # Deep indigo
    
    # Swirling currents of crimson & plum
    noise = create_noise_layer(W, H, 20, 3)
    swirl_mask = (noise * deep_mask) > 0.45
    img = apply_watercolor_wash(img, swirl_mask.astype(np.float32), (175, 55, 80), opacity=0.55, blur_radius=15) # Plum crimson
    img = apply_watercolor_wash(img, (noise * deep_mask) > 0.6, (220, 120, 60), opacity=0.5, blur_radius=12) # Hidden flame
    
    return add_paper_vignette(img)


def render_m013_rest_guilt():
    """M-013: 无法休息的内疚 (Hammock in willow branches, clock dissolving into golden dandelion seeds)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Soft olive & mint riverbank wash
    ground = np.clip((y_coords - H*0.5) / (H*0.4), 0, 1)
    img = apply_watercolor_wash(img, ground, (150, 175, 140), opacity=0.5)
    
    # 2. Willow branches framing from above
    willow = np.zeros((H, W), dtype=np.float32)
    for x in range(0, W, 35):
        w_len = int(H*0.35 + math.sin(x/50.0)*80)
        willow[0:w_len, max(0, x-4):min(W, x+4)] = 1.0
    img = apply_watercolor_wash(img, willow, (115, 140, 105), opacity=0.5, blur_radius=7)
    
    # 3. Hammock curved between trees
    hx, hy = int(W*0.5), int(H*0.64)
    ham_mask = np.zeros((H, W), dtype=np.float32)
    for x in range(int(W*0.25), int(W*0.75)):
        curve_y = int(hy + ((x - hx)/(W*0.25))**2 * 50)
        ham_mask[max(0, curve_y-15):min(H, curve_y+15), x] = 1.0
    img = apply_watercolor_wash(img, ham_mask, (180, 150, 115), opacity=0.7, blur_radius=8)
    
    # 4. Golden dandelion seeds floating into the sky
    seeds = np.zeros((H, W), dtype=np.float32)
    for _ in range(35):
        sx = random.randint(int(W*0.3), int(W*0.85))
        sy = random.randint(int(H*0.15), int(H*0.5))
        sdist = ((x_coords - sx)/12)**2 + ((y_coords - sy)/12)**2
        seeds = np.maximum(seeds, np.clip(1.0 - sdist, 0, 1))
    img = apply_watercolor_wash(img, seeds, (245, 215, 95), opacity=0.85, blur_radius=4) # Golden seeds
    
    return add_paper_vignette(img)


def render_m014_hard_to_ask_help():
    """M-014: 难以说出需要 (Two hands reaching across twilight, glowing golden dewdrop between)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Dusky violet and misty charcoal twilight
    twilight = np.clip(1.0 - (y_coords / H)*0.6, 0, 1)
    img = apply_watercolor_wash(img, twilight, (120, 115, 145), opacity=0.55)
    
    # 2. Hand reaching from left
    left_hand = np.zeros((H, W), dtype=np.float32)
    for x in range(0, int(W*0.44)):
        hy = int(H*0.52 + math.sin(x/40.0)*15)
        left_hand[max(0, hy-30):min(H, hy+30), x] = 1.0
    img = apply_watercolor_wash(img, left_hand, (185, 155, 140), opacity=0.7, blur_radius=12)
    
    # 3. Hand reaching from right
    right_hand = np.zeros((H, W), dtype=np.float32)
    for x in range(int(W*0.56), W):
        hy = int(H*0.52 + math.cos(x/40.0)*15)
        right_hand[max(0, hy-30):min(H, hy+30), x] = 1.0
    img = apply_watercolor_wash(img, right_hand, (175, 145, 135), opacity=0.7, blur_radius=12)
    
    # 4. Floating glowing golden dewdrop suspended between fingertips
    dx, dy = int(W*0.5), int(H*0.52)
    ddist = ((x_coords - dx)/26)**2 + ((y_coords - dy)/34)**2
    dew_mask = np.clip(1.0 - ddist, 0, 1)
    # Glow halo
    glow_dist = ((x_coords - dx)/90)**2 + ((y_coords - dy)/90)**2
    glow_mask = np.clip(1.0 - glow_dist, 0, 1)
    
    img = apply_watercolor_wash(img, glow_mask, (255, 230, 160), opacity=0.55, blur_radius=20)
    img = apply_watercolor_wash(img, dew_mask, (255, 245, 190), opacity=0.95, blur_radius=4)
    
    return add_paper_vignette(img)


def render_m015_dilemma():
    """M-015: 进退两难的摇摆 (Canoe resting at the quiet fork between two gentle streams)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Soft jade green island in the middle
    island_mask = np.zeros((H, W), dtype=np.float32)
    ix, iy = int(W*0.5), int(H*0.35)
    idist = ((x_coords - ix)/180)**2 + ((y_coords - iy)/140)**2
    island_mask = np.clip(1.0 - idist, 0, 1)
    img = apply_watercolor_wash(img, island_mask, (125, 155, 120), opacity=0.6, blur_radius=16)
    
    # 2. Two streams curving around the island into a calm pool
    water = np.clip((y_coords - H*0.4) / (H*0.5), 0, 1)
    img = apply_watercolor_wash(img, water, (140, 175, 190), opacity=0.55)
    
    # 3. Small wooden canoe resting peacefully in still eddy
    cx, cy = int(W*0.5), int(H*0.68)
    cdist = ((x_coords - cx)/90)**2 + ((y_coords - cy)/28)**2
    canoe_mask = np.clip(1.0 - cdist, 0, 1)
    img = apply_watercolor_wash(img, canoe_mask, (110, 80, 60), opacity=0.8, blur_radius=6) # Rich wood canoe
    
    # Gentle ripple ring around canoe
    rdist = np.sqrt(((x_coords - cx))**2 + ((y_coords - cy)*2.5)**2)
    c_ripple = np.clip(1.0 - np.abs(rdist - 110)/12.0, 0, 1)
    img = apply_watercolor_wash(img, c_ripple, (200, 225, 235), opacity=0.45, blur_radius=5)
    
    return add_paper_vignette(img)


def render_m016_loneliness():
    """M-016: 不被理解的孤独 (Small cozy cottage with warm glowing window by misty dusk lake)"""
    img = create_paper_texture(W, H)
    y_coords, x_coords = np.mgrid[0:H, 0:W]
    
    # 1. Deep dusk twilight across lake and distant hills
    dusk = np.clip(1.0 - (y_coords / H)*0.5, 0, 1)
    img = apply_watercolor_wash(img, dusk, (90, 85, 120), opacity=0.6) # Deep purple dusk
    
    # Lake below
    lake = np.clip((y_coords - H*0.55) / (H*0.45), 0, 1)
    img = apply_watercolor_wash(img, lake, (70, 95, 120), opacity=0.6)
    
    # 2. Quiet cottage silhouette by the shoreline
    cot_mask = np.zeros((H, W), dtype=np.float32)
    cot_mask[int(H*0.52):int(H*0.68), int(W*0.35):int(W*0.65)] = 1.0
    # roof triangle
    for y in range(int(H*0.42), int(H*0.52)):
        prog = (y - H*0.42) / (H*0.1)
        w_half = int(W*0.16 * prog)
        cot_mask[y, int(W*0.5 - w_half):int(W*0.5 + w_half)] = 1.0
    img = apply_watercolor_wash(img, cot_mask, (45, 45, 55), opacity=0.8, blur_radius=8)
    
    # 3. Warm golden circular window glowing inside
    wx, wy = int(W*0.5), int(H*0.58)
    wdist = ((x_coords - wx)/28)**2 + ((y_coords - wy)/28)**2
    win_mask = np.clip(1.0 - wdist, 0, 1)
    # Window glow reflection onto lake water
    ref_mask = np.zeros((H, W), dtype=np.float32)
    for y in range(int(H*0.68), int(H*0.88)):
        prog = (y - H*0.68) / (H*0.2)
        ref_mask[y, int(wx - 25 - prog*15):int(wx + 25 + prog*15)] = 1.0 - prog*0.5
        
    img = apply_watercolor_wash(img, ref_mask, (245, 190, 75), opacity=0.45, blur_radius=12) # Golden reflection
    img = apply_watercolor_wash(img, win_mask, (255, 230, 120), opacity=0.95, blur_radius=5) # Window light
    
    return add_paper_vignette(img)


# --------------------------------------------------------------------------
# Main Execution Dispatcher
# --------------------------------------------------------------------------

RENDERERS = {
    "M-003": render_m003_fear_starting,
    "M-004": render_m004_exhausted,
    "M-005": render_m005_self_blame,
    "M-006": render_m006_fear_rejection,
    "M-008": render_m008_peer_pressure,
    "M-009": render_m009_imposter_syndrome,
    "M-010": render_m010_ungrounded,
    "M-011": render_m011_judged_by_others,
    "M-012": render_m012_pretending_stable,
    "M-013": render_m013_rest_guilt,
    "M-014": render_m014_hard_to_ask_help,
    "M-015": render_m015_dilemma,
    "M-016": render_m016_loneliness,
}

if __name__ == "__main__":
    print(f"Starting procedural OH-card watercolor rendering for {len(RENDERERS)} cards...")
    for card_id, fn in RENDERERS.items():
        out_path = os.path.join(OUTPUT_DIR, f"{card_id}.png")
        print(f"  Rendering {card_id}...")
        img = fn()
        img.save(out_path, format="PNG", quality=95)
        print(f"  [OK] Saved {out_path} ({os.path.getsize(out_path):,} bytes)")
    print("\n[SUCCESS] All 13 procedural OH-card watercolor artworks generated successfully!")
