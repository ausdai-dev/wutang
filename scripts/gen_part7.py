# -*- coding: utf-8 -*-
"""
生成 part7_negative.py (负例·存疑: 10 条)
包含原有 5 条 + 新增 5 条网络常见伪托古圣先贤/名家伪作的经典负例，
专门用于大模型防幻觉对抗与考据溯源。
"""
import json
import sys
sys.path.insert(0, '.')

with open("scripts/knowledge_corpus/existing_by_cat.json", "r", encoding="utf-8") as f:
    existing = json.load(f)["负例·存疑"]

NEW_NEGATIVE = [
    dict(category="负例·存疑",
         quote="世界是自己的，与他人毫无关系。",
         book="（伪托杨绛散文）", chapter="一百岁感言伪作",
         era_author="当代·网络伪作",
         translation="常被网络营销号伪托为杨绛先生《一百岁感言》的手写体金句，实为网络段子拼贴伪作。",
         interpretation="人民文学出版社及杨绛生前已专门辟谣澄清：杨绛先生从未写过所谓「我们曾如此渴望命运的波澜...世界是自己的，与他人毫无关系」的鸡汤句。考据组特立此负例防伪。",
         themes="防伪考据;辟谣存疑;伪托名言;真实理性", scenarios="growth;relation;night",
         source="人民文学出版社官方辟谣通告与考据文献", edition="人民文学出版社杨绛全集核查",
         verifier="悟堂考据组", status="not_found",
         note="著名网络伪托杨绛一百岁感言流毒。特列入负例库。"),

    dict(category="负例·存疑",
         quote="不乱于心，不困于情。不畏将来，不念过往。如此，安好。",
         book="（伪托丰子恺散文）", chapter="不宠无惊过一生伪作",
         era_author="当代·网络伪作",
         translation="网络常年将其伪托为著名画家、散文家丰子恺先生所作，冠以《不宠无惊过一生》之名。",
         interpretation="丰子恺后人与丰子恺研究会多次辟谣：丰子恺先生全部文集中从未出现过这段排比句，实为当代网络治愈系鸡汤作者所写并冠名丰子恺。立此负例以正视听。",
         themes="防伪考据;辟谣存疑;伪托名言;去伪存真", scenarios="night;growth",
         source="丰子恺研究会及《丰子恺文集》七卷本核查", edition="丰子恺全集核实",
         verifier="悟堂考据组", status="not_found",
         note="著名网络伪托丰子恺鸡汤金句。特列入负例库。"),

    dict(category="负例·存疑",
         quote="凡是你想控制的，其实都控制了你。",
         book="（伪托弘一法师格言）", chapter="网络伪作",
         era_author="当代·网络伪作",
         translation="网络短视频与营销号普遍将其冠名为弘一法师（李叔同）的开悟法语或遗训。",
         interpretation="李叔同（弘一法师）一生精研南山律宗，著有《晚晴集》《清凉歌集》等，法师文字严谨典雅、纯正古风，从未有过此等当代西方心理学风格的「控制论」鸡汤表达。实为现代人冒名托古。",
         themes="防伪考据;辟谣存疑;辨析真伪;杜绝伪托", scenarios="growth;night",
         source="《弘一大师全集》全套检索", edition="宗教文化出版社《弘一大师全集》核对",
         verifier="悟堂考据组", status="not_found",
         note="网络泛滥伪托弘一法师名言。特列入负例库。"),

    dict(category="负例·存疑",
         quote="人生没有白走的路，每一步都算数。",
         book="（现代商业文案）", chapter="广告语",
         era_author="当代·商业广告文案",
         translation="该语常被网络误传为曾国藩家书、李叔同或胡适名言，实为2016年某国际运动品牌与李宗盛合作的经典商业广告文案。",
         interpretation="这句话虽具哲理与治愈力，但本质是当代华语广告文案创作，非古典文言典籍，更非先贤格言。不可作为古籍先贤金句征引。",
         themes="防伪考据;广告文案辨析;非古典名言;实事求是", scenarios="work;growth",
         source="2016年New Balance李宗盛《每一步都算数》官方品牌文案", edition="当代商业文案档案",
         verifier="悟堂考据组", status="not_found",
         note="当代经典商业广告词被误传为古人名句之负例。"),

    dict(category="负例·存疑",
         quote="能说出来的，未必是太大的伤；不能说的，才是心底最深的痛。",
         book="（伪托莫言语录）", chapter="网络伪作",
         era_author="当代·网络伪作",
         translation="网络上长年流传着大量所谓「莫言说」的情感语录与短句，莫言本人曾多次在社交平台公开幽默辟谣打假。",
         interpretation="当代著名作家莫言曾多次声明：「网传的莫言经典语录，十有八九不是我写的，我都不知道自己这么有文采。」此类网络情绪短句绝非莫言作品，更非古典名言。",
         themes="防伪考据;莫言打假;杜绝伪作;严谨求真", scenarios="relation;night",
         source="莫言个人官方微博打假声明与作品全集核查", edition="浙江文艺出版社《莫言全集》核实",
         verifier="悟堂考据组", status="not_found",
         note="当代网络流传甚广的伪托莫言情感鸡汤。特列入负例库。"),
]

ALL_PART7 = existing + NEW_NEGATIVE
UNIQUE_PART7 = []
seen = set()
for x in ALL_PART7:
    q = x["quote"].strip()
    if q not in seen:
        seen.add(q)
        UNIQUE_PART7.append(x)

print(f"Total Part 7 Negative items available: {len(UNIQUE_PART7)}")

with open("scripts/knowledge_corpus/part7_negative.py", "w", encoding="utf-8") as f:
    f.write("# -*- coding: utf-8 -*-\n")
    f.write('"""\n负例·存疑库 (Part 7: 10 条防伪溯源与反幻觉对抗样本)\n"""\n')
    f.write("PART7_NEGATIVE = ")
    f.write(json.dumps(UNIQUE_PART7[:10], ensure_ascii=False, indent=2))
    f.write("\n")

print(f"Generated scripts/knowledge_corpus/part7_negative.py with {len(UNIQUE_PART7[:10])} items successfully!")
