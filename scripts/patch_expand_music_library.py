# -*- coding: utf-8 -*-
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "frontend", "_template.html")

NEW_OPTIONS = (
    '<select id="sleepTrackSelect">'
    '<option value="0">行云流水</option>'
    '<option value="1">禅境冥想</option>'
    '<option value="2">秋雨箏韻</option>'
    '<option value="3">秋雨琴簫合奏</option>'
    '<option value="4">枕畔温煦</option>'
    '<option value="5">空灵入梦</option>'
    '<option value="6">夜幕归宁</option>'
    '<option value="7">海潮摇篮</option>'
    '<option value="8">眠琴微语</option>'
    '</select>'
)

OLD_OPTIONS = (
    '<select id="sleepTrackSelect">'
    '<option value="0">行云流水</option>'
    '<option value="1">禅境冥想</option>'
    '<option value="2">秋雨箏韻</option>'
    '<option value="3">秋雨琴簫合奏</option>'
    '</select>'
)

NEW_SCOPE_TRACKS = """      {
        name: '秋雨琴簫合奏',
        stroke: '#A8E6CF',
        secondary: '#7E6B5A',
        aura: 'rgba(168, 230, 207, ',
        status: '秋雨琴簫合奏 · 琴箫和鸣，万籁自息入梦',
        h1: 0.88, h2: 1.76, h3: 0.52
      },
      {
        name: '枕畔温煦',
        stroke: '#F4A261',
        secondary: '#E76F51',
        aura: 'rgba(244, 162, 97, ',
        status: '枕畔温煦 · 暖意入怀，倦意舒展渐浓',
        h1: 0.85, h2: 1.6, h3: 0.45
      },
      {
        name: '空灵入梦',
        stroke: '#B39DDB',
        secondary: '#7E57C2',
        aura: 'rgba(179, 157, 219, ',
        status: '空灵入梦 · 空灵悠远，随风轻飏入梦',
        h1: 0.65, h2: 1.3, h3: 0.55
      },
      {
        name: '夜幕归宁',
        stroke: '#64B5F6',
        secondary: '#42A5F5',
        aura: 'rgba(100, 181, 246, ',
        status: '夜幕归宁 · 夜幕轻垂，晚籁自安息心',
        h1: 0.92, h2: 1.84, h3: 0.48
      },
      {
        name: '海潮摇篮',
        stroke: '#4DD0E1',
        secondary: '#26A69A',
        aura: 'rgba(77, 208, 225, ',
        status: '海潮摇篮 · 潮涌如息，枕浪安澜入眠',
        h1: 0.72, h2: 1.44, h3: 0.38
      },
      {
        name: '眠琴微语',
        stroke: '#E8D7B8',
        secondary: '#D4B896',
        aura: 'rgba(232, 215, 184, ',
        status: '眠琴微语 · 琴音轻抚，心绪归平渐恬',
        h1: 1.15, h2: 2.3, h3: 0.6
      }
    ];"""

OLD_SCOPE_TRACKS = """      {
        name: '秋雨琴簫合奏',
        stroke: '#A8E6CF',
        secondary: '#7E6B5A',
        aura: 'rgba(168, 230, 207, ',
        status: '秋雨琴簫合奏 · 琴箫和鸣，万籁自息入梦',
        h1: 0.88, h2: 1.76, h3: 0.52
      }
    ];"""

NEW_BGM_TRACKS = """      {
        id: 'autumn_rain_qinxiao',
        name: '秋雨琴簫合奏',
        subtitle: 'Autumn Rain Qin & Xiao',
        src: 'assets/audio/autumn_rain_qinxiao.m4a',
        fallbackSrc: 'assets/audio/秋雨琴簫合奏.m4a',
        desc: '琴箫和鸣 · 虚室生白'
      },
      {
        id: 'cozy_bedtime_warmth',
        name: '枕畔温煦',
        subtitle: 'Cozy Bedtime Warmth',
        src: 'assets/audio/cozy_bedtime_warmth.m4a',
        fallbackSrc: 'assets/audio/Cozy Bedtime Warmth.m4a',
        desc: '暖意入怀 · 倦意舒安'
      },
      {
        id: 'ethereal_sleep_drift',
        name: '空灵入梦',
        subtitle: 'Ethereal Sleep Drift',
        src: 'assets/audio/ethereal_sleep_drift.m4a',
        fallbackSrc: 'assets/audio/Ethereal Sleep Drift.m4a',
        desc: '空灵悠远 · 随风入梦'
      },
      {
        id: 'nightfall_serenity',
        name: '夜幕归宁',
        subtitle: 'Nightfall Serenity',
        src: 'assets/audio/nightfall_serenity.m4a',
        fallbackSrc: 'assets/audio/Nightfall Serenity.m4a',
        desc: '夜幕轻垂 · 晚籁自安'
      },
      {
        id: 'ocean_breeze_lullaby',
        name: '海潮摇篮',
        subtitle: 'Ocean Breeze Lullaby',
        src: 'assets/audio/ocean_breeze_lullaby.m4a',
        fallbackSrc: 'assets/audio/Ocean Breeze Lullaby.m4a',
        desc: '潮涌如息 · 枕浪安澜'
      },
      {
        id: 'slumber_piano_whispers',
        name: '眠琴微语',
        subtitle: 'Slumber Piano Whispers',
        src: 'assets/audio/slumber_piano_whispers.m4a',
        fallbackSrc: 'assets/audio/Slumber Piano Whispers.m4a',
        desc: '琴音轻抚 · 心绪归平'
      }
    ];"""

OLD_BGM_TRACKS = """      {
        id: 'autumn_rain_qinxiao',
        name: '秋雨琴簫合奏',
        subtitle: 'Autumn Rain Qin & Xiao',
        src: 'assets/audio/autumn_rain_qinxiao.m4a',
        fallbackSrc: 'assets/audio/秋雨琴簫合奏.m4a',
        desc: '琴箫和鸣 · 虚室生白'
      }
    ];"""

OLD_COMMENT = "包含《行云流水》《禅境冥想》《秋雨箏韻》《秋雨琴簫合奏》四首东方禅意音轨，支持自动循环轮播"
NEW_COMMENT = "包含《行云流水》《禅境冥想》《秋雨箏韻》《秋雨琴簫合奏》《枕畔温煦》《空灵入梦》《夜幕归宁》《海潮摇篮》《眠琴微语》九首东方禅意与助眠音轨，支持自动循环轮播"

def main():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 更新 select 下拉框
    if OLD_OPTIONS in content:
        content = content.replace(OLD_OPTIONS, NEW_OPTIONS)
        print("[ok] 已更新 sleepTrackSelect 9 首曲目选项")
    else:
        print("[-] sleepTrackSelect 选项未变更或已是最新")

    # 2. 更新 sleepOscilloscope 示波器曲目谱系
    if OLD_SCOPE_TRACKS in content:
        content = content.replace(OLD_SCOPE_TRACKS, NEW_SCOPE_TRACKS)
        print("[ok] 已更新 sleepOscilloscope.SCOPE_TRACKS 9 首示波器特征")
    else:
        print("[-] sleepOscilloscope.SCOPE_TRACKS 未变更或已是最新")

    # 3. 更新 bgmEngine.TRACKS 曲目库
    if OLD_BGM_TRACKS in content:
        content = content.replace(OLD_BGM_TRACKS, NEW_BGM_TRACKS)
        print("[ok] 已更新 bgmEngine.TRACKS 9 首完整音频配置")
    else:
        print("[-] bgmEngine.TRACKS 未变更或已是最新")

    # 4. 更新注释
    if OLD_COMMENT in content:
        content = content.replace(OLD_COMMENT, NEW_COMMENT)

    with open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("[ok] frontend/_template.html 曲库扩充完成")

if __name__ == "__main__":
    main()
