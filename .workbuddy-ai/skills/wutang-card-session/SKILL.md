---
name: wutang-card-session
description: 管理三张解忧牌（心境牌—东方智慧牌—行动牌）的交互流程、主题匹配、牌组筛选、换牌与会话状态。输入用户文本、主题标签、已选牌和风险状态；输出结构化卡牌会话数据对象。遵循 PRD 2.0 卡牌体系，严禁虚构牌库 ID 或做确定性命运预言。
---

# Skill 1 · 三张解忧牌会话管理（wutang-card-session）

> 悟堂·东方解忧处 PRD 2.0 核心卡牌调度技能。管理「看见自己—换个视角—走出一步」三张解忧牌的完整匹配与状态流转。

## 一、触发条件

用户从首页选择「抽一张今日觉察牌」或「我有件心事」后，系统完成风险前置判断（`risk_status == 'normal'`）时调用。若为高危风险，直接阻断，不得调用本 Skill。

## 二、输入参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `session_id` | string | 否 | 会话唯一标识（若无则自动生成 `WT-YYYYMMDD-XXX`） |
| `entry_mode` | string | ✅ | 入口模式：`card`（觉察牌入口）或 `direct_input`（心事输入入口） |
| `theme_tag` | string | 否 | 用户自选或推断的情境标签：`work` / `relation` / `night` / `growth` |
| `user_text` | string | 否 | 用户输入的困扰或在觉察牌后的补充文本 |
| `current_cards` | object | 否 | 当前已抽取或已展示的卡牌 ID 记录，用于换牌时排除重复 |
| `change_target` | string | 否 | 换牌目标：`mindset` / `wisdom` / `action` / 空（全量匹配） |
| `user_reaction` | string | 否 | 用户反馈：`resonates`（很像我）/ `partly_resonates`（有一点像）/ `changed_card`（换一张）/ `skip`（跳过） |

## 三、核心匹配与筛选规则

1. **结构化牌库约束**：
   - 心境牌来自 `knowledge/cards_mindset.json`（ID 格式 `M-XXX`）
   - 东方智慧牌来自 `knowledge/cards_wisdom.json`（ID 格式 `W-XXX`，且必须为 `verification_status == 'verified'`）
   - 行动牌来自 `knowledge/cards_action.json`（ID 格式 `A-XXX`）
   - **严禁大模型动态虚构不存在的牌库 ID**。

2. **主题优先与软性匹配**：
   - 若用户指定 `theme_tag`，优先从包含该 tag 的卡牌池中选取。
   - 若未选标签且提供了 `user_text`，通过关键词/语义相关度定位最契合的场景。
   - 随机仅作为反思入口，不具有任何命理、占卜、吉凶或确定性心理诊断属性。

3. **换牌（Change Card）机制**：
   - 仅替换用户请求更换的那张牌（如心境牌或行动牌），保持其余牌和已输入文本不变。
   - 优先在同主题牌池中选取未展示过的候选项；若牌池候选项耗尽，可选取泛化兜底牌并向用户温和说明。

4. **语言表达边界**：
   - 解释卡牌与用户的关联时，一律使用「可能」「可以试着看看」「或许」等温和、非确定性表达。
   - 严禁宣称「你抽到这张牌命中注定」「古人专门为你显灵」。

## 四、输出规范

输出必须为严格的 JSON 结构：

```json
{
  "session_id": "WT-20261016-001",
  "selected_theme": "relation",
  "theme_label": "松绑 · 关系与边界",
  "entry_mode": "card",
  "cards": {
    "mindset": {
      "card_id": "M-001",
      "title": "总想让所有人满意",
      "front_text": "我是不是很久没有认真问过自己，真正想要的是什么？",
      "follow_up_question": "最近有没有一件事，你其实不愿意做，却因为担心别人失望而答应了？",
      "resonance_status": "resonates"
    },
    "wisdom": {
      "card_id": "W-001",
      "title": "求诸己",
      "original_text": "君子求诸己，小人求诸人。",
      "source_title": "《论语》",
      "source_section": "卫灵公",
      "source_ref": "CLASSIC-001",
      "verification_status": "verified",
      "modern_interpretation": "君子把力气花在自己能掌控的事情上，小人总把期待寄托在别人身上……"
    },
    "action": {
      "card_id": "A-002",
      "title": "给自己一点时间",
      "front_text": "下次遇到需要立即答应的请求时，先说「我考虑一下，再回复你」。",
      "estimated_minutes": 1,
      "steps": [
        "遇到请求时暂停 3 秒，不立刻答应",
        "回复一句缓冲语：「我先确认下手头安排，稍后回复你」",
        "私下评估自己的真实精力与意愿，再做决定"
      ],
      "alternative_action": "如果已经答应了，允许自己发消息补充：「我刚才看了下时间，可能只能协助部分内容」。"
    }
  },
  "session_status": "completed"
}
```
