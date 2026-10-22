---
name: wutang-wellbeing-assessment
description: 心境健康自评执行与确定性计分守门人。严格执行 PRD 3.0 专业审核门禁，严禁模型自由估算分数。
version: 1.0.0
---

# Skill: wutang-wellbeing-assessment

## 用途与职责
1. 查询与验证当前获准上线的自评量表注册表（`instrument_registry.json`）。
2. 未获批准或未通过专业审核的量表强制返回 `disabled_until_approved`。
3. 严格使用确定性代码（Python / JavaScript 规则引擎）进行问卷计分，彻底杜绝 LLM 算分幻觉或动态调整计分常模。
4. 挂载经专业审核的结果解释文案（低/中/高压力），附带清晰的非临床诊断免责声明。
5. 高危题目监测：一旦命中自伤或极度超载条件，立即触发独立安全求助流程，不被普通总分稀释。

## 输入格式
```json
{
  "instrument_id": "pss-10",
  "answers": [2, 3, 2, 2, 2, 3, 2, 1, 2, 2],
  "consent_to_record": true
}
```

## 输出格式
```json
{
  "assessment_id": "AS-20261019-7b3d",
  "instrument_id": "pss-10",
  "instrument_name": "知觉心理压力量表 (PSS-10)",
  "scoring_type": "deterministic",
  "total_score": 21,
  "score_range": "14-26",
  "level": "moderate",
  "level_label": "中度压力",
  "interpretation": "你近期体验到了生活中的不可控感或挑战，情绪与精力有所消耗，建议有意识安排身心休息与微行动调适。",
  "is_safety_flagged": false,
  "disclaimer": "自评用于自我了解与进一步求助决策，不能当作疾病诊断或医疗处方。"
}
```
