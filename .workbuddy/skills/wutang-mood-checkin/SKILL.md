---
name: wutang-mood-checkin
description: 处理用户每日心境签到，保存自选情绪、精力与主观压力感受，不作疾病推断或负面标签。
version: 1.0.0
---

# Skill: wutang-mood-checkin

## 用途与职责
管理「每日心境签到」数据流：
1. 记录用户主动勾选的心境标签（平静、充实、疲惫、焦虑、烦躁、失落等）。
2. 记录精力水平与主观感知压力（很轻、较轻、一般、较大、很大）。
3. 记录可选的一句话自述心语。
4. 严格遵守用户授权开关（仅在用户明确同意时保存于本地历史）。
5. 推荐一张契合心境的觉察卡或微行动，绝对不给用户贴心理疾病或性格缺陷标签。

## 输入格式
```json
{
  "user_local_date": "2026-10-19",
  "mood_tags": ["tired", "anxious"],
  "energy_level": "low",
  "perceived_stress": "high",
  "note": "今天项目汇报，神经紧绷了一整天",
  "consent_to_save": true
}
```

## 输出格式
```json
{
  "checkin_id": "MC-20261019-a1b2",
  "status": "saved",
  "summary": "记录已安全保存至本地成长日历",
  "recommended_card_id": "M-004",
  "gentle_note": "听见了你今天的高负荷，辛苦了。今晚允许自己早点休息，外界的事明天再说。"
}
```
