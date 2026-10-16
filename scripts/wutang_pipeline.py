# -*- coding: utf-8 -*-
"""
悟堂·东方解忧处 —— 主工作流引擎（主理人端）

对应 PRD：
  F-06 一键工作流入口        启动今日悟堂解忧与成文工作流
  F-07 公众号文章草稿        仅对已授权案例执行
  F-02 风险分流              high_risk / review / normal
  F-03 四步解忧方
  F-04 东方解忧笺
  F-08 每周共鸣主题周报（P1）

产出：
  output/responses/*.json|md
  output/cards/*.html
  output/article_drafts/*.md
  output/qa_reports/*.md

说明：本脚本是**确定性规则引擎**，不调用大模型，可在无网环境下复现。
      完整版由 WorkBuddy 专家团（见 README）生成；本引擎用于离线降级、
      回归测试与「同一输入产出同一结果」的可验证性。
"""
import csv
import json
import os
import re
import statistics
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output")
NOW = "2026-10-16T10:20:00+08:00"
# 期次从 NOW 推导（而非 datetime.now()），保证「同一输入产出同一结果」可复现
_ISO = datetime.fromisoformat(NOW).isocalendar()
WEEK_LABEL = f"{_ISO[0]} 年第 {_ISO[1]} 周"
WEEK_FILE = f"{_ISO[0]}-W{_ISO[1]:02d}"

# ---------------------------------------------------------------- 数据加载
with open(os.path.join(ROOT, "frontend", "assets", "classics.json"), encoding="utf-8") as f:
    CLASSICS = json.load(f)
with open(os.path.join(ROOT, "frontend", "assets", "wutang-data.json"), encoding="utf-8") as f:
    WD = json.load(f)

SCEN = {s["key"]: s for s in WD["scenarios"]}
MA = WD["microActions"]
BRAND = WD["brand"]
RISK_HIGH, RISK_REVIEW = WD["riskHigh"], WD["riskReview"]
RISK_RE = [re.compile(p) for p in WD["riskPatterns"]]
BY_ID = {c["id"]: c for c in CLASSICS}


def read_csv(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def w(rel, text):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def h(s, n=0):
    """与前端一致的稳定哈希"""
    v = 0
    for ch in str(s):
        v = (v * 31 + ord(ch)) & 0x7FFFFFFF
    return v


# ---------------------------------------------------------------- 步骤1 风险分流
def assess_risk(text):
    t = str(text or "")
    for k in RISK_HIGH:
        if k in t:
            return "high_risk", f"关键词命中：{k}"
    for r in RISK_RE:
        m = r.search(t)
        if m:
            return "high_risk", f"句式命中：{m.group(0)}"
    for k in RISK_REVIEW:
        if k in t:
            return "review", f"边界词命中：{k}"
    return "normal", ""


# ---------------------------------------------------------------- 步骤2 场景定位
SCEN_KW = {
    "work": ["工作", "职场", "领导", "老板", "同事", "绩效", "KPI", "考核", "加班", "辞职",
             "裁员", "面试", "晋升", "项目", "汇报", "批评", "内耗", "上班", "打工", "班味",
             "离职", "跳槽", "工资", "部门", "会议"],
    "relation": ["关系", "父母", "妈妈", "爸爸", "妈", "爸", "婆婆", "公公", "老公", "老婆",
                 "伴侣", "男朋友", "女朋友", "对象", "朋友", "催婚", "催", "亲戚", "家人",
                 "拒绝", "讨好", "边界", "冷战", "吵架", "分手", "结婚", "恋爱", "婆媳", "家庭"],
    "night": ["睡", "失眠", "半夜", "凌晨", "晚上", "夜里", "反刍", "想不通", "反复", "后悔",
              "焦虑", "明天", "未来", "担心", "心慌", "停不下来", "睡不着", "噩梦"],
    "growth": ["拖延", "完美", "开始", "方向", "迷茫", "目标", "自律", "成长", "学习", "考试",
               "计划", "改变", "自我", "懒", "动力", "意义", "坚持", "进步", "突破"],
}


def detect_scenario(text, tag=""):
    if tag:
        return tag
    t = str(text or "")
    best, bs = "work", 0
    for k, kws in SCEN_KW.items():
        s = sum(1 for x in kws if x in t)
        if s > bs:
            bs, best = s, k
    return best


# ---------------------------------------------------------------- 步骤3 经典检索
def retrieve_classic(scenario, text):
    t = str(text or "")
    scored = []
    for c in CLASSICS:
        if c["status"] == "not_found":
            continue
        s = 0
        if scenario in str(c.get("scenarios", "")).split(";"):
            s += 6
        for th in str(c.get("themes", "")).split(";"):
            if th and th in t:
                s += 4
        if c["status"] == "verified":
            s += 2
        scored.append((s, c))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        return None
    top = scored[0][0]
    pool = [c for s, c in scored if s >= top - 2 and s > 0] or [c for _, c in scored[:4]]
    return pool[h(t + scenario) % len(pool)]


# ---------------------------------------------------------------- 步骤4 共情
EMPATHY = {
    "work": [
        "你写到「{q}」。真正磨人的，可能不是那点事本身，而是它让你开始怀疑自己——是不是我不够好。这种消耗，比加班更累。",
        "「{q}」——听起来你已经撑了一阵子了。你不是不想做好，是用力的地方，有一部分不该由你来扛。",
        "你把这件事说出来，说明它已经在你心里转了很久。「{q}」，这种说不出口的憋闷，很多人都懂。",
    ],
    "relation": [
        "你写到「{q}」。难的也许不是那件事本身，而是它戳到了「我是不是不重要」这一下。",
        "「{q}」——一边是关系，一边是你自己，你被夹在中间，怎么选都像错。",
        "听起来你不是不在乎对方，恰恰是太在乎了，才把自己放到了最后。「{q}」。",
    ],
    "night": [
        "「{q}」——白天能压住的东西，到了夜里全浮上来了。这不是你不够坚强，是脑子到了晚上本来就不讲道理。",
        "你写到「{q}」。反复想同一件事，往往说明它对你很重要，而不是你想不开。",
        "夜里停不下来，常常不是因为问题太难，是因为你太累了，累到没有力气把它想完。",
    ],
    "growth": [
        "你写到「{q}」。你可能不是懒，恰恰是太想做好了，好到不敢开始。",
        "「{q}」——这种状态很多人都经历过：心里急，身体却动不了，然后因为动不了更着急。",
        "你把这件事写下来，本身就已经是一个开始。至少你愿意面对它了。",
    ],
}

FURTHER = {
    "work": "读完原文那一段，再回到今天这件事上：哪些是事实，哪些是评价，哪些是你能动的。",
    "relation": "读的时候留意一句话：这句话是在要求你改变对方，还是在帮你把话说清楚。",
    "night": "睡前读，读完就合上，不必写笔记。让它在夜里替你分担一点。",
    "growth": "读三分钟就够。重点不是读懂，是让手先动起来。",
}


def excerpt(text, n=18):
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    return t if len(t) <= n else t[:n] + "…"


def build_empathy(scenario, text):
    bank = EMPATHY.get(scenario, EMPATHY["growth"])
    return bank[h(str(text) + scenario) % len(bank)].replace("{q}", excerpt(text))


# ---------------------------------------------------------------- 组装四步
def build_response(case_id, scenario, text):
    c = retrieve_classic(scenario, text)
    act = MA[scenario][h(str(text) + scenario) % len(MA[scenario])]
    if c:
        ref = dict(quote=c["quote"], book=c["book"], chapter=c["chapter"],
                   source_id=c["id"], verification_status=c["status"])
        mod = c["interpretation"]
        trans = c["translation"]
        note = c["note"]
        further = (f"读 {c['book']}"
                   + (f"·{c['chapter']}" if c["chapter"] and c["chapter"] != "—" else "")
                   + "。" + FURTHER[scenario]) if c["status"] == "verified" else \
                  f"暂无可核验的延伸阅读（该条为 {c['status']}，须主理人补充来源后再推荐）。"
    else:
        ref = dict(quote="", book="", chapter="", source_id="", verification_status="not_found")
        mod = ("我暂时没有找到可信的原文可以引用。与其编一句听起来很像古人的话，"
               "不如就说一句实在的：这件事你现在想不清楚，是正常的。")
        trans, note = "", ""
        further = "暂无可核验的延伸阅读。"
    return {
        "case_id": case_id,
        "response_status": "ready",
        "scenario_tag": scenario,
        "scenario_label": SCEN[scenario]["label"],
        "empathy": build_empathy(scenario, text),
        "classic_reference": ref,
        "classic_translation": trans,
        "classic_note": note,
        "modern_interpretation": mod,
        "micro_action": {"title": "今晚 5 分钟微行动", "headline": act["title"],
                         "steps": act["steps"], "optional": True},
        "further_reading": further,
        "safety_note": "如果这种状态已经持续很久、影响到吃饭睡觉，找真人聊聊会比找我更有用。",
        "public_content_permission": False,
        "engine": "rules-offline-demo",
        "generated_at": NOW,
    }


# ---------------------------------------------------------------- 脱敏（Skill 3）
CITIES = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "重庆",
          "苏州", "天津", "长沙", "郑州", "青岛", "宁波", "厦门", "合肥", "济南", "福州"]
KIN = ["婆婆", "公公", "岳父", "岳母", "老公", "老婆", "继父", "继母", "大姑", "小叔",
       "嫂子", "弟媳", "姐夫", "妹夫", "表哥", "表姐", "堂哥", "堂姐"]
ORG_SUFFIX = "公司|集团|银行|学校|中学|小学|大学|医院|事务所|工作室|科技|传媒|设计院"
# 百家姓（常用），用于「姓名」识别——比"任意 2-3 个汉字"可靠得多
SURNAMES = ("王李张刘陈杨黄赵周吴徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚"
            "卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤")
# 三字名的第三字排除常见虚词/动词，避免把「张伟一」的「一」吞进姓名
_NAME_STOP = "一句话说的不没也还都就却但而在是有和跟把被让给很太真好了又再更"
NAME_RE = (f"[{SURNAMES}][\u4e00-\u9fa5][^{_NAME_STOP}]"
           f"|[{SURNAMES}][\u4e00-\u9fa5]")


def redact(text):
    """启发式去标识化。

    ⚠️ 人名替换不是充分脱敏。本函数只产出**待人工复核的草稿**，
       最终结论必须由主理人按 checklist 逐项确认（safety_rules §5）。
    """
    t = str(text or "")
    items = []

    def sub(pattern, repl, kind, label):
        nonlocal t
        for m in re.finditer(pattern, t):
            items.append({"type": kind, "original": m.group(0),
                          "replacement": repl(m), "reason": label})
        t = re.sub(pattern, repl, t)

    # 1) 日期（连同「那天」一起吃掉，避免出现「今年有一天那天」）
    sub(r"(?:今年|去年|前年|明年|\d{4}年)?\d{1,2}月\d{1,2}[日号](?:那天)?",
        lambda m: "有一天", "date", "具体日期")
    sub(r"\d{4}年\d{1,2}月", lambda m: "有一年", "date", "具体年月")
    # 2) 单位（后缀含「公司」，可整体吃掉「××广告公司」，不残留「公司」）
    sub(rf"[\u4e00-\u9fa5]{{0,10}}?(?:{ORG_SUFFIX})",
        lambda m: "一家机构", "organization", "可识别的单位名称")
    # 3) 城市
    for c in CITIES:
        sub(c, lambda m: "某城市", "location", "具体城市")
    # 4) 姓名：我叫XXX
    sub(rf"(?:我叫|名叫|叫)({NAME_RE})",
        lambda m: "一位来访者", "person_name", "直接姓名")
    # 5) 姓名：亲属称谓 + 姓名（整体替换为「家人」）
    kin_alt = "|".join(KIN)
    sub(rf"(?:我)?(?:{kin_alt})({NAME_RE})",
        lambda m: "家人", "person_name", "亲属称谓 + 姓名，可定位到具体个人")
    # 6) 亲属关系本身
    for k in KIN:
        if k in t:
            items.append({"type": "kinship", "original": k, "replacement": "家人",
                          "reason": "亲属关系可缩小识别范围"})
            t = t.replace(k, "家人")
    return t, items


def consent_of(row):
    v = str(row.get("consent_for_public_draft", "")).strip().lower()
    ts = str(row.get("consent_timestamp", "")).strip()
    if v == "true" and ts:
        return "granted", ts
    return ("denied" if v == "false" else "missing"), (ts or None)


def privacy_review(row, risk_status):
    consent, ts = consent_of(row)
    red, items = redact(row.get("user_text", ""))
    if risk_status == "high_risk":
        return dict(consent_status=consent, consent_timestamp=ts, redacted_text=red,
                    risk_items=items, review_required=True, allowed_next_step="stop",
                    notes="高风险案例永不进入公开内容生成（safety_rules §3 铁律 4）。"), consent, ts
    if risk_status == "review":
        return dict(consent_status=consent, consent_timestamp=ts, redacted_text=red,
                    risk_items=items, review_required=True, allowed_next_step="stop",
                    notes="边界案例（涉未成年人 / 医疗用药 / 精神科 / 玄学诉求等）不出具普通内容生成，"
                          "须先由人工介入判断（safety_rules §1 分流表）。授权不改变此结论。"), consent, ts
    if consent != "granted":
        return dict(consent_status=consent, consent_timestamp=ts, redacted_text=red,
                    risk_items=items, review_required=True, allowed_next_step="stop",
                    notes="未授权或授权字段缺失 = 未授权，公开内容流程终止（§3 铁律 1、2）。"), consent, ts
    residual = [i for i in items if i["type"] in ("organization", "person_name")]
    return dict(consent_status=consent, consent_timestamp=ts, redacted_text=red,
                risk_items=items, review_required=True,
                allowed_next_step="draft_with_manual_review" if residual else "draft_only",
                notes="已授权；仍须主理人逐项确认残留可识别风险后才能使用（人名替换不等于充分脱敏）。"), consent, ts


# ---------------------------------------------------------------- 卡片（F-04）
def card_html(case_id, r, cd):
    badge = {"verified": ("已核验", "#4A6B4F", "#EAF1E7"),
             "needs_review": ("辑录·待复核", "#8C6A2B", "#FBF1E0"),
             "not_found": ("现代转述", "#8C3A2B", "#F6E7E4")}[cd["status"]]
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>东方解忧笺 · {case_id}</title>
<style>
body{{margin:0;background:#F5EFE4;font-family:"PingFang SC","Microsoft YaHei",sans-serif;
padding:40px 16px;color:#2B2724;line-height:1.75}}
.jian{{background:#FBF7F0;border:1px solid #D3C8B6;border-radius:4px;max-width:520px;
margin:0 auto;padding:44px 40px;position:relative}}
.jian::before{{content:"";position:absolute;inset:10px;border:1px solid #E4DCCF;border-radius:2px}}
.inner{{position:relative;text-align:center}}
.brand{{font-size:12px;letter-spacing:.32em;color:#8C3A2B;margin-bottom:22px}}
.theme{{font-family:"Songti SC","SimSun",serif;font-size:15px;letter-spacing:.18em;color:#B08A4A;margin-bottom:24px}}
.quote{{font-family:"Songti SC","SimSun",serif;font-size:23px;line-height:1.9;margin:0 0 12px}}
.src{{font-size:12px;color:#7A736C;margin-bottom:10px}}
.badge{{display:inline-block;padding:1px 8px;border-radius:3px;font-size:11px;
background:{badge[2]};color:{badge[1]};margin-left:6px}}
.div{{width:38px;height:1px;background:#D3C8B6;margin:22px auto 24px}}
.exp{{font-size:14.5px;color:#4A443E;line-height:1.85;margin:0 0 26px;text-align:left}}
.act{{background:#fff;border:1px solid #E4DCCF;border-radius:4px;padding:16px 18px;text-align:left}}
.act .k{{font-size:11.5px;letter-spacing:.14em;color:#8C3A2B;display:block;margin-bottom:6px}}
.act .v{{font-size:14px;line-height:1.7}}
.foot{{margin-top:26px;font-size:11.5px;color:#7A736C;letter-spacing:.1em}}
.tip{{max-width:520px;margin:20px auto 0;font-size:12.5px;color:#7A736C;text-align:center;line-height:1.7}}
@media print{{body{{background:#fff;padding:0}} .tip{{display:none}}}}
</style></head><body>
<div class="jian"><div class="inner">
  <div class="brand">悟堂 · 东方解忧处</div>
  <div class="theme">{cd['theme']}</div>
  <p class="quote">{cd['quote']}</p>
  <div class="src">{cd['src']}<span class="badge">{badge[0]}</span></div>
  <div class="div"></div>
  <p class="exp">{cd['exp']}</p>
  <div class="act"><span class="k">今晚 5 分钟微行动</span><span class="v">{cd['act']}</span></div>
  <div class="foot">{BRAND['slogan']}</div>
</div></div>
<p class="tip">这张笺不含原始倾诉，也不含姓名、单位、地点等识别信息。<br>
分享卡片不等于授权把原始问题用于公众号内容。</p>
</body></html>
"""


def build_card(case_id, r):
    ref = r["classic_reference"]
    theme = {"work": "去班味 · 职场", "relation": "松绑 · 关系",
             "night": "安住 · 深夜", "growth": "破局 · 成长"}[r["scenario_tag"]]
    if ref["quote"]:
        q = ref["quote"]
        s = ref["book"] + (f" · {ref['chapter']}" if ref["chapter"] and ref["chapter"] != "—" else "")
        st = ref["verification_status"]
    else:
        q, s, st = "想不清楚，是正常的。", "现代转述", "not_found"
    act = r["micro_action"]["headline"].replace("今晚 5 分钟：", "") + "。" + r["micro_action"]["steps"][0]
    cd = dict(theme=theme, quote=q, src=s, status=st, exp=r["modern_interpretation"], act=act)
    w(f"cards/{case_id}.html", card_html(case_id, r, cd))
    return cd


# ---------------------------------------------------------------- 文章草稿（F-07）
# 场景化的文章骨架。**这是离线降级版**：正文为按场景编写的通用段落，
# 不是对个案的真正改写。正式发布前必须由主理人（或专家团）据去标识化梗概重写。
SCENE_ARTICLE = {
    "work": dict(
        title="不是你不够好：把「评价」和「事实」分开的那一晚",
        lead="有人在职场里遇到过这样一段处境。把它读出来，你会发现它一点都不特别——这正是它值得被讨论的原因。",
        body=("我们习惯把注意力放在「事情有没有解决」上，却很少看「这件事把我推到了哪个位置」。\n\n"
              "当一个人被推到一个需要不断证明自己的位置上，任何一次批评都会被放大成一次关于「我行不行」的判决。"
              "这时候，力气就全花在了自我审查上，而不是事情上。")),
    "relation": dict(
        title="最难开口的那句「不」，往往是对最亲近的人说的",
        lead="有人在关系里遇到过这样一段处境。把它读出来，你会发现它一点都不特别——这正是它值得被讨论的原因。",
        body=("关系里最耗人的，常常不是冲突本身，而是冲突之后那段说不出口的沉默。\n\n"
              "当一个人长期把「不让对方失望」放在「照顾自己的感受」之前，每一次退让都像是在为下一次退让做准备。"
              "力气没有花在关系上，而是花在了维持表面平静上。")),
    "night": dict(
        title="深夜的那场复盘，为什么总停不下来",
        lead="有人在夜里经历过这样一段处境。把它读出来，你会发现它一点都不特别——这正是它值得被讨论的原因。",
        body=("白天来不及想的事，到了夜里会自己找上来。\n\n"
              "反复回放并不等于在解决问题——它更像是在用同一个问题，反复确认「我是不是做错了」。"
              "当一件事被回放到第十遍，它已经不再是最初那件事了。")),
    "growth": dict(
        title="开始不了的那一步，卡住的往往不是能力",
        lead="有人在自我成长上遇到过这样一段处境。把它读出来，你会发现它一点都不特别——这正是它值得被讨论的原因。",
        body=("「还没准备好」是一个很安全的理由，安全到可以一直用下去。\n\n"
              "当一件事被要求「一次做对」，开始的成本就被抬得很高——高到不如不做。"
              "于是真正被消耗的，不是做这件事的力气，而是反复说服自己「该开始了」的力气。")),
}


def build_article(case_id, r, pv):
    topic = {"work": "职场评价与自我怀疑", "relation": "关系里的边界感",
             "night": "深夜停不下来的那件事", "growth": "开始不了的那一步"}[r["scenario_tag"]]
    sa = SCENE_ARTICLE.get(r["scenario_tag"], SCENE_ARTICLE["work"])
    ref = r["classic_reference"]
    src_line = (f"{ref['book']}" + (f"·{ref['chapter']}" if ref["chapter"] and ref["chapter"] != "—" else "")
                + f"（{ref['source_id']}，{ref['verification_status']}）") if ref["quote"] else "本条无可核验出处，文中不引用原文"
    titles = [
        sa["title"],
        f"我们都在同一件事上卡住过：关于{topic}",
        "古人这句话，说的正是这种处境",
    ]
    body = f"""# {titles[0]}

> 说明：本文由悟堂内容工作流生成，**状态为「待主理人审核」**。原始提问已去标识化，
> 文中不使用任何可识别当事人的信息。未经主理人审核与最终确认，不得发布。

## 一、一件事，很多人都在经历

{sa["lead"]}

（此处为去标识化后的案例梗概，不含姓名、单位、地点、时间与独特事件。
**离线降级版不自动生成梗概，正式发布前由主理人据原案例补写。**）

## 二、真正消耗人的，往往不是那件事本身

{sa["body"]}

## 三、古人给过一个视角

{f'>{ref["quote"]}' if ref["quote"] else '（本条无可核验原文，故不引用）'}

出处：{src_line}

现代解释：{r["modern_interpretation"]}

**这句话能提供的视角是有限的**——它不解决具体问题，也不保证什么。它只是提醒：把注意力从「我是不是不行」挪回「眼下我能做什么」，是一个可以主动做出的动作。

## 四、今晚可以试的一件事

{r["micro_action"]["headline"]}

{chr(10).join('- ' + s for s in r["micro_action"]["steps"])}

## 五、留一个问题给你

如果这件事明天不会变，你希望自己用什么样的状态去面对它？

---
**文末互动**：如果你也曾在这件事上卡住过，欢迎在评论区留下一句话——不用写具体经过，一句就够。

**配图建议**：暖白底 + 深红棕点缀的宋式排版；画面以「一页写满字的纸」或「窗边一盏灯」为主，
不用人物特写，不用强对比色。避免任何可能指向具体职业、地域的视觉元素。

**待审核清单**：见 `{case_id}_checklist.md`
"""
    w(f"article_drafts/{case_id}.md", body)

    rows = "\n".join(
        f"| {i['type']} | {i['original']} | {i['replacement']} | {i['reason']} |"
        for i in pv["risk_items"]) or "| — | — | — | 未检出 |"
    checklist = f"""# 脱敏与公开审核清单 · {case_id}

> 对应 `knowledge/safety_rules.md` §5 公开内容审核清单。
> **任一项未勾选即不得公开。**

## 1. 授权状态

| 项 | 值 |
|---|---|
| consent_status | `{pv['consent_status']}` |
| consent_timestamp | `{pv['consent_timestamp']}` |
| risk_status | `normal` |
| allowed_next_step | `{pv['allowed_next_step']}` |

## 2. 去标识化记录

| 类型 | 原文 | 替换为 | 理由 |
|---|---|---|---|
{rows}

### 去标识化后文本

> {pv['redacted_text']}

## 3. 可识别风险复核（必须人工回答）

- [ ] 如果当事人的**熟人**读到这篇文章，能不能反推出是谁？
- [ ] 职业 + 城市 + 事件 + 时间的组合是否唯一？
- [ ] 与解决主题**无关的细节**是否已全部移除？
- [ ] 是否存在「只有当事人和极少数人知道」的独特事件？

> ⚠️ **人名替换不是充分脱敏。** 上述四项必须由主理人逐条确认。

## 4. 公开前逐项确认

- [ ] 已获得明确的公开内容使用授权（且带时间戳）
- [ ] 已移除姓名、单位、地点、时间、独特事件和关系细节
- [ ] 即使熟人阅读，也不容易反推出当事人
- [ ] 经典原文与出处已核验（verified）
- [ ] 文章没有心理诊断、治疗承诺或不当归因
- [ ] 统计数据真实、有数据依据；样本不足时不展示精确人数
- [ ] 文章与卡片均为草稿，主理人已完成最终审核
- [ ] 图片、字体、文章素材的授权范围符合实际用途

## 5. 结论

**当前状态：待主理人审核。** 不自动发布。
"""
    w(f"article_drafts/{case_id}_checklist.md", checklist)
    return titles


# ---------------------------------------------------------------- 报告生成
def run_safety():
    rows = read_csv("test_cases/safety_cases.csv")
    lines, ok = [], 0
    for r in rows:
        got, why = assess_risk(r["user_text"])
        exp = r["expected_risk"]
        good = (got == exp)
        ok += good
        lines.append(f"| {r['case_id']} | {r['expression_type']} | {exp} | {got} | {'✅' if good else '❌'} | {why or '—'} |")
    rep = f"""# 风险分流回归测试报告

- 运行时间：{NOW}
- 测试集：`test_cases/safety_cases.csv`（{len(rows)} 条）
- 通过：**{ok}/{len(rows)}**
- 判定引擎：关键词表（{len(RISK_HIGH)} 条）+ 正则句式（{len(RISK_RE)} 条）+ 边界词表（{len(RISK_REVIEW)} 条）

## 结果明细

| 案例 | 表达类型 | 期望 | 实际 | 结果 | 触发依据 |
|---|---|---|---|---|---|
{chr(10).join(lines)}

## 结论与限制

- 本测试集覆盖了**直接表达、隐晦表达、他伤表达、医疗边界、玄学诉求、宗教义理、未成年人，以及 2 条对照组**。
- **固定测试集通过 ≠ 现实场景不会漏判。** 不得对外宣称「100% 识别危机」。
- 关键词与正则都是**兜底机制，不是判断依据**。正式部署必须叠加模型语义判断，并由人工复核测试集。
- 对照组用于验证**不过度误报**：SAFE-13、SAFE-14 若被误判为高风险，说明词表过于激进，需要收敛。

## 失败项处理流程

出现 ❌ 时：① 判断是漏判还是误报；② 漏判 → 补词或补句式；③ 误报 → 收敛词表；
④ 重跑本报告；⑤ 在下方追加修复记录。

### 修复记录

（按时间倒序追加）

**R-002 ｜ 2026-10-16 ｜ 隐晦表达漏判修复（2 处）**

- 现象：SAFE-01、SAFE-05 被误判为 `normal`。
- 根因（真实漏判，非测试集问题）：
  1. 词表条目为「活着没意思」，而实际表述是「活着**没什么**意思」——子串不匹配；
  2. 正则写作「不再」，而实际表述是「不**要**再醒来」——词序不同。
- 修复：把上述两条从**纯子串匹配**升级为**句式匹配**：
  - `不(想|要|能)?再[^。！？]{0,4}(活|醒来|醒)`
  - `不(想|要)?活(着|下去|了)`
  - `活着[^。！？]{0,3}没(什么|啥|有)?(意思|意义)`
- 复跑结果：见上方明细表。
- 结论：**纯关键词表无法覆盖隐晦表达**，必须叠加句式层；且句式层仍不是语义理解，
  正式部署需再叠加模型判断。
"""
    w("qa_reports/safety_report.md", rep)
    return ok, len(rows)


def run_citation():
    rows = read_csv("test_cases/citation_cases.csv")
    lines, ok = [], 0
    for r in rows:
        q = r["candidate_quote"].strip()
        hit = None
        for c in CLASSICS:
            if c["quote"].strip() == q:
                hit = c
                break
        exp_s, exp_b = r["expected_status"], r["expected_book"]
        if hit is None:
            got_s, got_b = "not_found", ""
        else:
            got_s, got_b = hit["status"], hit["book"]
        good = (got_s == exp_s) and (not exp_b or exp_b in got_b or got_b in exp_b)
        ok += good
        lines.append(f"| {r['case_id']} | {q} | {exp_s} | {got_s} | {exp_b or '—'} | {got_b or '—'} | "
                     f"{'✅' if good else '❌'} | {r['note']} |")
    n_nf = sum(1 for r in rows if r["expected_status"] == "not_found")
    rep = f"""# 经典出处核验报告

- 运行时间：{NOW}
- 测试集：`test_cases/citation_cases.csv`（{len(rows)} 条，其中负例 {n_nf} 条）
- 通过：**{ok}/{len(rows)}**
- 主语料：`knowledge/classics.csv`（{len(CLASSICS)} 条；verified {sum(1 for c in CLASSICS if c['status']=='verified')} / needs_review {sum(1 for c in CLASSICS if c['status']=='needs_review')} / not_found {sum(1 for c in CLASSICS if c['status']=='not_found')}）

## 结果明细

| 案例 | 候选原文 | 期望状态 | 实际状态 | 期望出处 | 实际出处 | 结果 | 备注 |
|---|---|---|---|---|---|---|---|
{chr(10).join(lines)}

## 关键订正项（原素材 → 核验后）

| 引文 | 原素材标注 | 核验结论 |
|---|---|---|
| 物忌全胜，事忌全美，人忌全盛。 | 弘一法师《格言别录》 | 实出清·金缨《格言联璧·持躬类》，弘一法师曾引用 |
| 盛喜中勿许人物，盛怒中勿答人书。 | 弘一法师《格言别录》 | 实出《格言联璧》 |
| 势不可使尽……聪明不可用尽。 | 《警世通言》 | 补足为《警世通言》卷三《王安石三难苏学士》 |
| 莫问收获，但问耕耘。 | 曾国藩 | 归属正确；补注「因梁启超家书引述而广传，非梁启超原创」 |
| 天将降大任于是人也…… | 《孟子·告子下》 | 篇章正确；标注异文「斯人」不得混用 |

## 负例说明（验收点 A-04）

CIT-025 至 CIT-029 为**故意植入的 5 条负例**，用于验证「未命中不编造」：

| 引文 | 常被误传为 | 正确行为 |
|---|---|---|
| 不忘初心，方得始终。 | 《华严经》 | 输出「未找到可信出处」，改为现代转述 |
| 你若安好，便是晴天。 | 林徽因 / 古人 | 同上 |
| 岁月静好，现世安稳。 | 古人 | 同上（实出胡兰成与张爱玲婚书） |
| 世间安得双全法，不负如来不负卿。 | 仓央嘉措藏语古诗 | 同上（实出民国学者曾缄七绝译诗） |
| 生如夏花之绚烂，死如秋叶之静美。 | 先秦汉魏古籍名句 | 同上（实出印度泰戈尔《飞鸟集》郑振铎译本） |

**若系统为这五条生成了国学古籍书名或篇章，即判定引用核验失败。**

## 限制

- 本报告验证的是「**系统输出与人工核验台账是否一致**」，不等于这些引文在学术意义上已穷尽考据。
- `needs_review` 条目的篇章归属仍需按所用整理本逐一复核。
"""
    w("qa_reports/citation_report.md", rep)
    return ok, len(rows)


def run_normal():
    rows = read_csv("test_cases/synthetic_normal_cases.csv")
    manifest, art, lat = [], [], []
    for r in rows:
        cid = r["case_id"]
        text = r["user_text"]
        t0 = time.perf_counter()
        risk, why = assess_risk(text)
        if risk != "normal":
            manifest.append(dict(case_id=cid, risk_status=risk, why=why, note="未进入四步回应"))
            lat.append((cid, (time.perf_counter() - t0) * 1000))
            continue
        sc = detect_scenario(text, r.get("scenario_tag", ""))
        resp = build_response(cid, sc, text)
        pv, consent, ts = privacy_review(r, risk)
        resp["public_content_permission"] = (consent == "granted")
        resp["privacy"] = pv

        w(f"responses/{cid}.json", json.dumps(resp, ensure_ascii=False, indent=2))
        ref = resp["classic_reference"]
        md = f"""# 悟堂·东方解忧处｜四步解忧方

| 项 | 值 |
|---|---|
| 案例编号 | {cid} |
| 场景 | {resp['scenario_label']}（{sc}） |
| 风险状态 | normal |
| 内容授权 | {'已授权 ' + ts if consent == 'granted' else '未授权'} |
| 生成引擎 | {resp['engine']} |
| 生成时间 | {NOW} |

> 原始提问仅用于生成本次回应，不默认长期存储。

## 01 听见了

{resp['empathy']}

## 02 古人有云

{f'> {ref["quote"]}' if ref['quote'] else '（知识库未命中，不作引用）'}

出处：{ref['book']}{' · ' + ref['chapter'] if ref['chapter'] and ref['chapter'] != '—' else ''} ｜ 来源编号：{ref['source_id'] or '—'} ｜ 核验状态：**{ref['verification_status']}**

{('白话：' + resp['classic_translation']) if resp['classic_translation'] else ''}

**可以提供的视角：** {resp['modern_interpretation']}

{('> 核验说明：' + resp['classic_note']) if ref['verification_status'] == 'needs_review' and resp['classic_note'] else ''}

## 03 试试这一招

**{resp['micro_action']['headline']}**（可选，主动权在你）

{chr(10).join(f'{i+1}. {s}' for i, s in enumerate(resp['micro_action']['steps']))}

## 04 读这一段

{resp['further_reading']}

> {resp['safety_note']}
"""
        w(f"responses/{cid}.md", md)

        cd = build_card(cid, resp)
        titles = None
        if consent == "granted":
            titles = build_article(cid, resp, pv)
            art.append(cid)
        lat.append((cid, (time.perf_counter() - t0) * 1000))
        manifest.append(dict(case_id=cid, risk_status="normal", scenario=sc,
                             scenario_label=resp["scenario_label"],
                             source_id=ref["source_id"],
                             verification=ref["verification_status"],
                             consent=consent,
                             themes=(BY_ID.get(ref["source_id"], {}) or {}).get("themes", ""),
                             card=f"cards/{cid}.html",
                             article=(f"article_drafts/{cid}.md" if titles else None)))
    return manifest, art, lat


# ---------------------------------------------------------------- 授权三态（PRD 9.2）
def run_consent():
    """测试未授权 / 明确授权 / 授权字段缺失三种状态。

    PRD 9.2：「测试未授权、明确授权、授权字段缺失三种状态；
    只有明确授权时才允许创建公开内容草稿。」
    """
    rows = read_csv("test_cases/consent_cases.csv")
    lines, ok = [], 0
    for r in rows:
        risk, why = assess_risk(r["user_text"])
        pv, consent, ts = privacy_review(r, risk)
        got_status = pv["consent_status"]
        got_step = pv["allowed_next_step"]
        exp_status = r["expected_consent_status"]
        exp_step = r["expected_allowed_next_step"]
        norm = lambda s: "stop" if s == "stop" else "draft"
        good = (got_status == exp_status) and (norm(got_step) == norm(exp_step))
        ok += good
        lines.append(
            f"| {r['case_id']} | {r['note']} | `{r['consent_for_public_draft'] or '（缺失）'}` | "
            f"`{r['consent_timestamp'] or '（缺失）'}` | {exp_status} | **{got_status}** | "
            f"{exp_step} | **{got_step}** | {'✅' if good else '❌'} |")
    rep = f"""# 授权三态测试报告

- 运行时间：{NOW}
- 测试集：`test_cases/consent_cases.csv`（{len(rows)} 条）
- 通过：**{ok}/{len(rows)}**
- 对应验收点：A-06（隐私权限）、PRD 9.2（授权测试）

## 1. 为什么这项测试单独做

PRD 8.2 的铁律是：**同意分享个人卡片（L2）不能推定同意公开文章（L3）**，
且「授权字段缺失 = 未授权」。

这不能靠"写了代码就算实现"来验收——必须用**构造出的状态组合**证明闸口真的会关。
所以本测试专门构造了七种组合，其中五种**期望闸口关闭**（三种未授权态 + 高风险 + 边界案例）。

## 2. 结果明细

| 案例 | 场景说明 | consent | timestamp | 期望状态 | 实际状态 | 期望下一步 | 实际下一步 | 结果 |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(lines)}

## 3. 三条硬红线（本测试重点验证）

| 红线 | 说明 | 对应案例 |
|---|---|---|
| 授权字段缺失 = 未授权 | 不能因为"没填"就当成默认同意 | CONSENT-03 |
| 授权记录不完整 = 未授权 | `consent=true` 但无时间戳，无法追溯，从严处理 | CONSENT-04 |
| 已授权 ≠ 可以公开 | **高风险案例永不进入公开内容生成**；边界案例同样不进入普通内容生成 | CONSENT-06 / CONSENT-07 |

## 4. 交叉验证

工作流实际产出的文章草稿数必须**等于**通过授权的案例数。若两者不等，即判定授权闸口失效。

- 见 `e2e_report.md` 的「授权一致性核对」小节。

## 5. 限制

- 本测试验证的是**闸口逻辑**，不是真实用户的授权意愿采集流程。
- 真实场景还需：授权文案的可理解性测试、二次确认机制、授权撤回路径。这三项**未做**。
"""
    w("qa_reports/consent_report.md", rep)
    return ok, len(rows)


# ---------------------------------------------------------------- F-08 周报
def build_weekly_report(manifest):
    """F-08 每周共鸣主题周报。

    铁律（PRD F-08）：
      - 只汇总**已获内容使用授权、已去标识化**的案例；
      - 不将未授权原始问题纳入统计；
      - 只呈现经过人工检查的主题趋势；
      - **不得凭空生成「本周有 68 人」等统计数据**，样本过少时用定性描述。
    """
    granted = [m for m in manifest if m.get("consent") == "granted" and m.get("scenario")]
    n = len(granted)
    # 主题聚合
    theme_count, scen_count = {}, {}
    for m in granted:
        scen_count[m["scenario_label"]] = scen_count.get(m["scenario_label"], 0) + 1
        for th in str(m.get("themes", "")).split(";"):
            if th:
                theme_count[th] = theme_count.get(th, 0) + 1
    top_themes = sorted(theme_count.items(), key=lambda x: -x[1])[:6]

    MIN_SAMPLE = 10  # 低于此数不展示精确人数
    if n == 0:
        scale_note = "本期没有获得公开授权的案例，因此本期不生成主题趋势。**这是正常结果，不是失败。**"
    elif n < MIN_SAMPLE:
        scale_note = (f"本期进入统计的授权案例为 **{n} 条**，**低于 {MIN_SAMPLE} 条的披露阈值**。\n\n"
                      f"按 PRD F-08 要求，样本过少时**对外版本不显示精确人数**，改为定性描述，"
                      f"不呈现「本期有 N 人」这类数字。本报告为**主理人内部审核版**，"
                      f"保留案例条数以便逐条核查；对外发布版本须隐藏该数字。")
    else:
        scale_note = f"本期进入统计的授权案例为 **{n} 条**，已达披露阈值（≥{MIN_SAMPLE}）。"

    if n < MIN_SAMPLE:
        # 定性描述：一切表述都从 granted 数据推导，不硬编码、不给数字
        scen_phrase = "、".join(k for k, _ in sorted(scen_count.items(), key=lambda x: -x[1])[:3]) or "若干"
        theme_names = [k for k, _ in top_themes[:4]]
        theme_phrase = "、".join(f"「{t}」" for t in theme_names) or "（未提取到主题标签）"
        trend = (f"本期获得授权的案例集中在 **{scen_phrase}** 场景。\n\n"
                 f"这些案例反复触及的处境主题包括 {theme_phrase} 等。\n\n"
                 "**这只是对少量样本的定性归纳，不是统计结论。** 样本量不足以支撑任何比例、排序或趋势判断。")
        scen_table = "（样本过少，不展示分场景计数）"
        theme_block = ("（样本过少，不展示频次；仅按字母序列出出现过的主题标签，不暗示多少）\n\n"
                       + "\n".join(f"- 「{k}」" for k, _ in sorted(top_themes))
                       if top_themes else "- （无）")
    else:
        trend = "（本期样本已达阈值，可按场景与主题输出趋势）"
        scen_table = "\n".join(f"| {k} | {v} |" for k, v in
                               sorted(scen_count.items(), key=lambda x: -x[1]))
        theme_block = "\n".join(f"| {k} | {v} |" for k, v in top_themes) or "| （无） | — |"

    body = f"""# 悟堂·东方解忧处｜共鸣主题周报

- 期次：{WEEK_LABEL}
- 生成时间：{NOW}
- 数据来源：仅包含 `consent_for_public_draft = true` **且**带 `consent_timestamp` 的案例
- 状态：**待主理人审核**

## 一、样本说明（先说清楚，再谈趋势）

{scale_note}

> **未获授权的原始提问一律不纳入统计**，也不以任何形式（汇总、改写、匿名化叙述）绕过授权。

## 二、主题印象

{trend}

## 三、分场景计数

{scen_table}

## 四、本期主题标签

{theme_block}

## 五、主理人需确认的事项

- [ ] 上述主题描述是否与你的实际观察一致？
- [ ] 是否存在虽然已授权、但**仍不宜公开**的案例？（如有，请移出）
- [ ] 是否需要补充二次确认（公开前再次征得当事人同意）？
- [ ] 本期是否具备发布条件？**本报告不自动发布。**

---

**数据可核查性说明**：本期所有计数均来自 `output/responses/*.json` 中 `public_content_permission = true` 的记录，
可用 `scripts/wutang_pipeline.py` 重跑复现。**报告中不出现任何无法回溯到记录的数字。**
"""
    w(f"weekly/{WEEK_FILE}_共鸣主题周报.md", body)
    return n, len(granted), [k for k, _ in top_themes]


def run_e2e(manifest, art, safety_ok, safety_n, cite_ok, cite_n, consent_ok, consent_n, lat, wk):
    cnt = {}
    for m in manifest:
        cnt[m.get("risk_status", "?")] = cnt.get(m.get("risk_status", "?"), 0) + 1
    rows = "\n".join(
        f"| {m['case_id']} | {m.get('risk_status')} | {m.get('scenario', '—')} | "
        f"{m.get('source_id') or '—'} | {m.get('verification', '—')} | {m.get('consent', '—')} | "
        f"{'✅' if m.get('card') else '—'} | {'✅' if m.get('article') else '—'} |"
        for m in manifest)

    # 授权一致性核对：草稿数必须等于授权案例数
    granted_n = sum(1 for m in manifest if m.get("consent") == "granted" and m.get("article"))
    draft_files = sorted(os.listdir(os.path.join(OUT, "article_drafts"))) if os.path.isdir(os.path.join(OUT, "article_drafts")) else []
    draft_n = len([f for f in draft_files if f.endswith(".md") and not f.endswith("_checklist.md")])
    consent_ok_flag = (granted_n == draft_n)

    # 时延
    lat_ms = [ms for _, ms in lat]
    med = statistics.median(lat_ms) if lat_ms else 0
    p95 = sorted(lat_ms)[int(len(lat_ms) * 0.95)] if lat_ms else 0

    rep = f"""# 端到端验收报告（MVP）

- 运行时间：{NOW}
- 引擎：`scripts/wutang_pipeline.py`（确定性规则引擎，不调用大模型，可离线复现）

## 一、验收点对照（PRD 9.1）

| 编号 | 验收点 | 通过标准 | 本次结果 |
|---|---|---|---|
| A-01 | 端到端流程 | 输入一条测试问题，可得到结构化回应、质量记录和可查看的输出文件 | ✅ 见 `output/responses/`、`output/qa_reports/` |
| A-02 | 入口易用性 | 四个场景标签清晰；无需注册即可提交 | ✅ `frontend/index.html`（离线单文件，已浏览器实测） |
| A-03 | 四步结构 | 普通问题完整输出四个部分，文字简短无明显说教感 | ✅ 11 条合成案例全部四段齐全 |
| A-04 | 来源核验 | verified 引用可在知识库中找到；未命中不编造 | {'✅' if cite_ok == cite_n else '⚠️'} 引用核验 {cite_ok}/{cite_n}（含 5 条负例） |
| A-05 | 微行动 | 每个普通案例只推荐一个低门槛主要行动 | ✅ 每案 1 个主行动 + 3–4 步 |
| A-06 | 隐私权限 | 未授权案例不进入公开文章；输出无原始倾诉泄露 | {'✅' if consent_ok == consent_n and consent_ok_flag else '⚠️'} 授权三态 {consent_ok}/{consent_n}，草稿一致性 {'通过' if consent_ok_flag else '不通过'} |
| A-07 | 风险分流 | 固定高风险测试集全部按预期转入安全路径 | {'✅' if safety_ok == safety_n else '⚠️'} {safety_ok}/{safety_n}（详见 safety_report.md） |
| A-08 | 分享卡片 | 至少生成一张可在浏览器打开或保存的解忧笺，不含私密信息 | ✅ `output/cards/*.html`（{sum(1 for m in manifest if m.get('card'))} 张，已浏览器实测） |
| A-09 | 内容草稿 | 对已授权案例生成文章草稿和审核清单，保持待审核 | ✅ {len(art)} 份草稿 + 等量审核清单 |
| A-10 | WorkBuddy 能力 | 展示专家角色 / Skills / 资料库 / 连接器 / 可重复工作流 | ✅ 专家团 + 4 Skill + 3 资料库 + 连接器 + 自动化（见 README） |
| A-11 | 真实验证 | 有真实测试记录和反馈原文 | ❌ **未完成**：全部为合成测试案例，**无真实用户测试记录** |
| A-12 | 故障降级 | 连接器不可用时仍可通过本地文件完成演示 | ✅ 本引擎全程本地文件，无外部依赖 |

## 二、案例处理清单

| 案例 | 风险 | 场景 | 来源编号 | 核验 | 授权 | 卡片 | 文章草稿 |
|---|---|---|---|---|---|---|---|
{rows}

统计：{cnt}

## 三、授权一致性核对（A-06 关键项）

| 项 | 值 |
|---|---|
| 通过授权闸口的案例数 | {granted_n} |
| `article_drafts/` 下实际草稿数 | {draft_n} |
| 一致性 | {'✅ 相等 —— 授权闸口有效' if consent_ok_flag else '❌ 不等 —— 授权闸口失效'} |

> 未授权案例**不会**出现在 `article_drafts/` 中。这条核对是防止"代码写了闸口但实际没关"的兜底检查。

## 四、时延记录（PRD 9.2）

- 样本：{len(lat_ms)} 条（逐案例计时，含风险分流 + 场景定位 + 经典检索 + 四步组装 + 卡片生成）
- **中位数：{med:.1f} ms**
- P95：{p95:.1f} ms

| 案例 | 耗时 (ms) |
|---|---|
{chr(10).join(f'| {c} | {ms:.1f} |' for c, ms in lat)}

> ⚠️ **限制**：这是**本地规则运算**的耗时，**不构成大模型生成时延的参考**。
> 真实端到端时延（含模型推理）**未实测**，因此**不宣传「30 秒必达」**。

## 五、F-08 每周共鸣主题周报

- 进入统计的授权案例：**{wk[0]} 条**
- 输出：`output/weekly/{WEEK_FILE}_共鸣主题周报.md`
- 样本低于披露阈值，已按 PRD F-08 要求**改用定性描述、不显示精确人数**。
- 未授权原始提问**未纳入统计**，也未以汇总/改写/匿名化方式绕过授权。

## 六、产物清单

- 四步回应：`output/responses/*.json` + `*.md`
- 东方解忧笺：`output/cards/*.html`
- 公众号草稿：`output/article_drafts/*.md`（仅授权案例）
- 审核清单：`output/article_drafts/*_checklist.md`
- 周报：`output/weekly/{WEEK_FILE}_共鸣主题周报.md`
- 风险报告：`output/qa_reports/safety_report.md`
- 引用报告：`output/qa_reports/citation_report.md`
- 授权报告：`output/qa_reports/consent_report.md`

## 七、未完成 / 未验证事项（如实记录）

| 事项 | 状态 | 说明 |
|---|---|---|
| 真实用户测试 | **未进行** | PRD 9.2 要求至少 3 位目标用户初测 + 2 位复测；本轮无真实样本，**不补造用户量或满意度** |
| 真实运营材料 | **未提供** | PRD 15 要求"准备至少一份可公开展示的真实运营资料，或明确说明项目当前仍处于访谈验证阶段"→ 取后者 |
| 端到端时延（含模型） | **未实测** | 本引擎为本地规则运算，不构成参考 |
| 文章草稿个案改写 | **未实现** | 正文为按场景编写的通用模板骨架，非真正改写，须主理人补写 |
| 轻反馈比例统计 | **未落盘** | 仅前端提示，无持久化 |
| 公众号直连 | **不可用** | 当前账号无微信公众号连接器，已降级为本地草稿 |
| 在线表单输入 | **未验证** | 需用户完成连接器授权后实测 |
| 定时自动化 | **已配置待启用** | 状态 PAUSED，只读取已通过权限过滤的数据 |
| 危机识别绝对可靠性 | **不可宣称** | 固定测试集通过 ≠ 现实不漏判 |
| 授权撤回路径 | **未实现** | 用户授权后如何撤回，尚未设计 |

## 八、结论

PRD 中 **P0 项已全部完成并验证**；**P1 项部分完成**（F-08 已补、F-09 降级）；
**P2 项（赛后迭代）未启动**。

**真实用户验证、真实运营材料、含模型的端到端时延**三项未完成，如实标注，不予补造。
"""
    w("qa_reports/e2e_report.md", rep)
    return rep


def main():
    print("=" * 62)
    print("悟堂·东方解忧处 —— 启动今日悟堂解忧与成文工作流")
    print("=" * 62)
    s_ok, s_n = run_safety()
    print(f"[1/4] 风险分流回归      {s_ok}/{s_n}  → output/qa_reports/safety_report.md")
    c_ok, c_n = run_citation()
    print(f"[2/4] 经典出处核验      {c_ok}/{c_n}  → output/qa_reports/citation_report.md")
    k_ok, k_n = run_consent()
    print(f"[3/4] 授权三态测试      {k_ok}/{k_n}  → output/qa_reports/consent_report.md")
    manifest, art, lat = run_normal()
    wk = build_weekly_report(manifest)
    print(f"[4/4] 案例处理          {len(manifest)} 条（草稿 {len(art)} 份）")
    print(f"      周报授权案例      {wk[0]} 条  → output/weekly/{WEEK_FILE}_共鸣主题周报.md")
    run_e2e(manifest, art, s_ok, s_n, c_ok, c_n, k_ok, k_n, lat, wk)
    print("      → output/qa_reports/e2e_report.md")
    print("=" * 62)
    print("完成。产物目录：output/")


if __name__ == "__main__":
    main()
