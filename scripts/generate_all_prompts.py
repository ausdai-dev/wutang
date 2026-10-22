# -*- coding: utf-8 -*-
"""
Generate English prompt mappings for all 96 Oriental Wisdom cards.
Ensures consistent Song dynasty ink wash, Gongbi delicacy, antique Xuan paper texture,
and strict negative constraints across the entire deck.
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_JSON = os.path.join(ROOT, "DOC", "cards_parsed.json")
OUT_JSON = os.path.join(ROOT, "DOC", "cards_english_prompts.json")

# Dictionary of specialized scene and subject translations for the cards
# to maintain poetic elegance and fidelity to the Chinese prompt.

PROMPT_MAP = {
    "04": {
        "name_en": "Present Moment",
        "scene_en": "Morning dewdrop suspended delicately on a fresh bamboo shoot along a misty stone path in a green bamboo grove. A subtle bare foot stepping gently on a mossy flagstone, soft dawn sunlight filtering through the bamboo leaves. Fine details, peaceful and clear.",
        "palette": "bamboo green, fresh tender green, warm rice paper white, misty grey",
        "pinyin": "04_dang_xia"
    },
    "05": {
        "name_en": "Rest and Return",
        "scene_en": "A peaceful Chinese scholar sitting naturally in a serene teahouse study on a woven rush mat. Outside the wooden lattice window, morning mist floats past bamboo stems. Inside, a low wooden table holds a single porcelain tea bowl. Warm, tranquil, low contrast.",
        "palette": "warm beige, chestnut brown, soft celadon, muted charcoal grey",
        "pinyin": "05_gui_xi"
    },
    "06": {
        "name_en": "Non-Attachment",
        "scene_en": "A gentle open hand gracefully letting go of a single autumn maple leaf, which drifts away on a soft breeze toward distant misty mountains. Minimalist strokes, vast negative space, peaceful acceptance of change.",
        "palette": "soft ochre red, pale celadon grey, antique paper warm white, light ink",
        "pinyin": "06_bu_zhi"
    },
    "07": {
        "name_en": "Warming the Cup",
        "scene_en": "Delicate steam gently rising from a small, warm celadon tea cup held carefully on a clean rustic wooden tea tray. A slender bamboo water ladle rests quietly beside a simple iron kettle. Intimate, unhurried, peaceful preparation.",
        "palette": "shadow celadon, warm wood brown, rice paper cream, soft tea mist grey",
        "pinyin": "07_wen_zhan"
    },
    "08": {
        "name_en": "Listening to the Kettle",
        "scene_en": "An antique cast-iron kettle simmering gently over faint glowing charcoal in a sunken hearth. Subtle spirals of steam curl softly into the quiet room. Outside the bamboo screen, gentle bamboo shadows sway.",
        "palette": "charcoal black, warm ember amber, antique paper beige, misty wash",
        "pinyin": "08_song_tao"
    },
    "09": {
        "name_en": "Single Flavor",
        "scene_en": "A single rustic ceramic tea cup sitting quietly on a natural rough flagstone. Pure clear tea liquor inside reflecting a sliver of soft morning light. A single camellia flower petal rests quietly nearby.",
        "palette": "warm amber tea brown, slate grey, off-white Xuan paper, subtle petal blush",
        "pinyin": "09_yi_wei"
    },
    "10": {
        "name_en": "Tea Leaves Unfolding",
        "scene_en": "A transparent or celadon bowl with fresh spring tea leaves slowly unfurling in clear hot water. Soft gentle water swirls, delicate leaf veins, quiet transformation and opening up.",
        "palette": "spring sprout green, pale jade, translucent water white, antique beige",
        "pinyin": "10_shu_zhan"
    },
    "11": {
        "name_en": "Resting the Cup",
        "scene_en": "A small stoneware tea cup placed gently on a weathered wooden table. A tea master's hand has just withdrawn, leaving a tranquil, still space between tea sips. Low afternoon light cast through paper window.",
        "palette": "tea brown, warm umber, rice paper white, soft shadow grey",
        "pinyin": "11_ting_zhan"
    },
    "12": {
        "name_en": "Gentle Aftertaste",
        "scene_en": "A quiet scholar sitting by an open courtyard veranda, holding a simple tea bowl and looking into a courtyard where rain has just stopped. Drops glistening on courtyard moss, lingering quiet sweetness.",
        "palette": "moss green, wet stone grey, pale warm paper, soft charcoal",
        "pinyin": "12_hui_gan"
    },
    "13": {
        "name_en": "Impermanence",
        "scene_en": "A fragile blossom petal drifting down onto a quiet stone bench where two teacups were shared. Faint ripples in a stone basin, soft wind moving through plum blossoms. Poetic beauty of passing time.",
        "palette": "faint blossom blush, weathered stone grey, warm paper cream, ink wash",
        "pinyin": "13_wu_chang"
    },
    "14": {
        "name_en": "Cherishing the Imperfect",
        "scene_en": "A cherished Song dynasty ceramic bowl with delicate golden repair lines (Kintsugi / Chinese gold lacquer repair), resting quietly on coarse linen. Honoring flaws and history as unique beauty.",
        "palette": "celadon green, antique gold lacquer line, unbleached linen beige, soft ink",
        "pinyin": "14_que_han"
    },
    "15": {
        "name_en": "Harmonious Meeting",
        "scene_en": "Two ancient scholar friends conversing quietly under a blooming crabapple tree in a tranquil courtyard, seated at a stone table with a Go board and tea cups. Natural harmony and deep mutual respect.",
        "palette": "pale crabapple pink, turquoise green, warm paper white, diluted ink",
        "pinyin": "15_he_yuan"
    },
    "16": {
        "name_en": "Reverence",
        "scene_en": "Two hands respectfully presenting a small wrapped gift or a sprig of plum blossoms with both palms open and humble posture. Gentle bows in ancient robes, deeply earnest and dignified.",
        "palette": "low-saturation cinnabar, warm rice paper, soft ink grey, tea brown",
        "pinyin": "16_jing_yi"
    },
    "17": {
        "name_en": "Kind Acceptance",
        "scene_en": "An elder scholar in flowing robes gently holding an umbrella over a young traveler under a soft spring drizzle by a river ferry. Tender, warm human compassion in an ink wash landscape.",
        "palette": "indigo blue, pale bamboo green, warm rain grey, antique paper",
        "pinyin": "17_ci_xin"
    },
    "18": {
        "name_en": "Shared Solitude",
        "scene_en": "Two scholars sitting apart on different benches along a misty mountain path, each gazing into the distant rolling clouds in companionable silence, neither disturbing the other's quiet peace.",
        "palette": "pine needle green, cloud mist white, pale charcoal, warm beige",
        "pinyin": "18_tong_ji"
    },
    "19": {
        "name_en": "Wu Wei (Non-Forcing)",
        "scene_en": "A clear mountain brook winding effortlessly around smooth granite boulders, flowing naturally along the contours of the valley without struggle or resistance. Water lilies and floating leaves.",
        "palette": "clear water blue-grey, moss green, river pebble grey, Xuan paper white",
        "pinyin": "19_wu_wei"
    },
    "20": {
        "name_en": "Softness Overcomes Hardness",
        "scene_en": "Persistent gentle water droplets dripping rhythmically from a cliff overhang onto a hard stone, slowly shaping a smooth indentation over centuries. Ethereal, patient power of yielding.",
        "palette": "slate grey, water droplet crystal white, moss green, antique beige",
        "pinyin": "20_rou_ren"
    },
    "21": {
        "name_en": "Knowing When to Stop",
        "scene_en": "A small wooden boat approaching a peaceful reed-lined shore and dropping anchor right at the water's edge before entering the turbulent open currents. Knowing contentment and boundaries.",
        "palette": "reed golden-brown, tranquil lake pale grey, misty sky, rice paper cream",
        "pinyin": "21_zhi_zhi"
    },
    "22": {
        "name_en": "Deep Stillness",
        "scene_en": "An ancient pine standing motionless in a secluded valley at dusk, completely undisturbed by the swirling mountain mists around it. Rooted deeply into ancient stone.",
        "palette": "deep pine green, twilight ink grey, pale gold horizon, warm paper",
        "pinyin": "22_gui_jing"
    },
    "23": {
        "name_en": "Emptiness and Fullness",
        "scene_en": "A graceful hollow bamboo grove swaying gently in the wind. The empty inner chambers of the bamboo allow it to bend without breaking in the mountain breeze.",
        "palette": "bamboo green, pale jade, misty morning white, warm paper tone",
        "pinyin": "23_xu_shi"
    },
    "24": {
        "name_en": "Following the Seasons",
        "scene_en": "An autumn landscape with wild geese flying in V-formation across a pale moonlit evening sky over ripening grain fields and quiet hills. Nature's unhurried rhythm.",
        "palette": "harvest ochre, moonlit silver white, ink wash grey, antique paper beige",
        "pinyin": "24_shun_shi"
    }
}

# Function to generate an appropriate prompt for any card
def get_card_prompt(card):
    cid = card["id"]
    if cid in PROMPT_MAP:
        info = PROMPT_MAP[cid]
        pinyin = info["pinyin"]
        prompt = (
            f"Chinese ink wash and Gongbi painting on antique Xuan paper, vertical 2:3 ratio. "
            f"{info['scene_en']} "
            f"Palette of {info['palette']}. "
            f"Clean composition, elegant negative space, masterwork quality, spiritual tranquility. "
            f"No text, no words, no characters, no seals, no signatures, no watermark."
        )
        return pinyin, prompt
    
    # Generic intelligent synthesis based on card scene and series
    name = card["name"]
    series = card["series"]
    scene = card["scene"]
    
    # Series specific styling
    series_style = {
        "禅心之境": "Zen tranquility, vast negative space, monk robes, mountain mist, ancient pine, stone lantern, quiet contemplation.",
        "一盏茶事": "Tea ceremony serenity, fine ceramic teaware, delicate steam, weathered wooden tea table, bamboo shadows, slow living.",
        "因缘相惜": "Heartfelt human connection, mutual respect, shared silence, gentle gifts, warmth, compassionate companionship.",
        "道法自然": "Taoist harmony with nature, flowing river, resilient bamboo, wind through pines, water shaping stone, effortless flow.",
        "君子修身": "Noble scholar virtue, plum blossom, orchid, inkstone, jade pendant, courtyard study, moral integrity and self-cultivation.",
        "山水人生": "Expansive landscape, solitary traveler on mountain path, ferry crossing, snow-dusted peaks, distant horizons, life journey."
    }
    
    # Pinyin conversion helper
    pinyin = f"{cid}_card"
    prompt = (
        f"Chinese ink wash and Gongbi painting on antique Xuan paper, vertical 2:3 ratio. "
        f"Subject: {scene}. Inspired by {series_style.get(series, 'traditional oriental landscape')}. "
        f"Warm rice-paper tone, diluted ink grey, mineral pigments (pine green, ochre, celadon). "
        f"Masterful composition, poetic atmosphere, refined texture. "
        f"No text, no words, no characters, no seals, no signatures, no watermark."
    )
    return pinyin, prompt

with open(SRC_JSON, "r", encoding="utf-8") as f:
    cards = json.load(f)

full_prompts = []
for c in cards:
    pinyin, prompt = get_card_prompt(c)
    full_prompts.append({
        "id": c["id"],
        "series": c["series"],
        "name": c["name"],
        "pinyin": pinyin,
        "prompt": prompt,
        "raw_scene": c["scene"]
    })

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(full_prompts, f, ensure_ascii=False, indent=2)

print(f"Generated {len(full_prompts)} prompts in {OUT_JSON}")
