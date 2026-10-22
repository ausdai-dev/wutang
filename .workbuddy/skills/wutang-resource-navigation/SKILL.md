---
name: wutang-resource-navigation
description: 经真实核验的心理援助专业资源导航检索与转介沟通摘要生成。
version: 1.0.0
---

# Skill: wutang-resource-navigation

## 用途与职责
1. 基于用户主动指定的地区（全国、北京、上海、广东、浙江等）筛选经过核验的专业心理资源。
2. 呈现公立精神卫生机构、24小时免费心理危机干预热线与专业机构，每条资源包含：
   - 官方名称、服务类型、官方联系电话/地址
   - 来源机构与最后核验日期（2026-10-19）
   - 服务时段与适用限制说明
3. 协助生成用户主动发起的「转介沟通摘要」（包含自述主诉、持续时间、自评结果及想向医生/咨询师咨询的关键问题），支持逐项编辑与一键复制，未经用户授权绝不自动发送第三方。

## 输入格式
```json
{
  "region": "北京",
  "service_type": "hotline",
  "need_referral_summary": false
}
```

## 输出格式
```json
{
  "total_found": 1,
  "resources": [
    {
      "resource_id": "RES-BJ-001",
      "region": "北京",
      "resource_name": "北京心理危机研究与干预中心",
      "service_type": "hotline",
      "contact_info": "010-82951332 / 800-810-1117",
      "source_url": "北京回龙观医院官方网站",
      "last_verified_at": "2026-10-19",
      "status": "verified"
    }
  ]
}
```
