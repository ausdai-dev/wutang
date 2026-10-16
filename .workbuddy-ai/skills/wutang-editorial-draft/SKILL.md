---
name: wutang-editorial-draft
description: 针对已获得明确授权、已充分脱敏且风险评估为 normal 的案例，生成公众号与共读文章草稿及合规审核清单。严禁处理未授权案例，所有产出均标记为「待主理人审核」，绝不自动公开发布。
---

# Skill 6 · 公众号文章草稿生成（wutang-editorial-draft）

> 悟堂内容工作室的内容生产技能。仅服务于已授权公共内容沉淀，是公共案例文章的合规草拟者。

## 一、前置阻断护栏（硬性铁律）

在执行本 Skill 前，必须满足：
1. `consent_for_public_draft === true` 且具备合法的 `consent_timestamp`；
2. 风险分流结果必须为 `normal`（高风险 `high_risk` 与边界 `review` 案例一律阻断，授权无效）；
3. 已经过 `privacy-consent-review` 彻底剥离姓名、单位、地点、事件细节等 PII。

**若前置条件未满足，立即终止执行，禁止输出草稿。**

## 二、输入参数

| 字段 | 来源 | 必填 | 说明 |
|---|---|---|---|
| `case_id` | 任务编号 | ✅ | 任务 ID（如 `WUTANG-SYN-004`） |
| `scenario` | 场景分类 | ✅ | `work` / `relation` / `night` / `growth` |
| `redacted_summary` | `privacy-consent-review` | ✅ | 泛化脱敏后的共性困扰梗概 |
| `classic_item` | `classic-citation-check` | ✅ | 已核验经典原文及篇章考据 |
| `micro_action` | 行动牌数据 | ✅ | 推荐的低门槛微行动 |
| `consent_timestamp` | 授权凭证 | ✅ | 用户确认授权时间戳 |

## 三、内容组织与八项合规复核

1. **结构要素**：
   - **推文标题**：温和、直击内耗痛点（如《最难开口的那句「不」，往往是对最亲近的人说的》）。
   - **引子**：描述普遍共性处境，不暴露个案隐私。
   - **文化回响**：引入经核验的传世古籍与先贤视角，原文与白话解析分层展现。
   - **微行动建议**：给读者一个今晚可在 5 分钟内尝试的行动切片。
   - **文末声明**：明确标注「本文案例已获当事人匿名共读授权，细节已做泛化脱敏处理；内容仅供日常情绪整理与反思，不替代专业心理咨询或医疗诊治」。

2. **八项合规复核清单**：
   - [x] 内容使用授权范围已取得正式确认
   - [x] 用户真实姓名及直接身份标识已剔除
   - [x] 单位/机构/学校等机构标识已替换或泛化
   - [x] 具体时间与地点信息已做模糊化处理
   - [x] 关系人及特殊事件细节已无法反向推导
   - [x] 经典引文出处及考据版本已核实无误
   - [x] 不含任何医学诊断、精神治疗暗示或绝对承诺
   - [x] 稿件状态明确标识为「待主理人审核」，不具备自动发布权限

## 四、输出格式

输出包含文章 Markdown 正文与结构化审核元数据：

```json
{
  "case_id": "WUTANG-SYN-004",
  "review_status": "pending_manual_review",
  "article_title": "最难开口的那句「不」，往往是对最亲近的人说的",
  "article_content": "# 最难开口的那句「不」...\n\n> 导语：...",
  "compliance_checklist": {
    "consent_verified": true,
    "pii_redacted": true,
    "citation_verified": true,
    "non_diagnostic": true,
    "manual_review_required": true
  }
}
```
