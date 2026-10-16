# 授权三态测试报告

- 运行时间：2026-10-16T10:20:00+08:00
- 测试集：`test_cases/consent_cases.csv`（7 条）
- 通过：**7/7**

## 结果明细

| 案例 | 场景说明 | consent | timestamp | 期望状态 | 实际状态 | 期望下一步 | 实际下一步 | 结果 |
|---|---|---|---|---|---|---|---|---|
| CONSENT-01 | 状态一：明确未授权 —— 不得进入文章草稿 | `false` | `（缺失）` | denied | **denied** | stop | **stop** | ✅ |
| CONSENT-02 | 状态二：明确授权（含时间戳）—— 允许生成草稿，但仍须待主理人审核 | `true` | `2026-10-16T09:30:00+08:00` | granted | **granted** | draft | **draft_only** | ✅ |
| CONSENT-03 | 状态三：授权字段缺失 —— 等同于未授权（PRD 8.2 铁律 2） | `（缺失）` | `（缺失）` | missing | **missing** | stop | **stop** | ✅ |
| CONSENT-04 | 边界：consent=true 但时间戳缺失 —— 授权记录不完整，从严视为未授权 | `true` | `（缺失）` | missing | **missing** | stop | **stop** | ✅ |
| CONSENT-05 | 边界：布尔值大小写容错，不应因大小写差异误判为未授权 | `TRUE` | `2026-10-16T10:00:00+08:00` | granted | **granted** | draft | **draft_only** | ✅ |
| CONSENT-06 | **关键红线**：即使已授权，高风险案例也永不进入公开内容生成（safety_rules §3 铁律 4） | `true` | `2026-10-16T10:05:00+08:00` | granted | **granted** | stop | **stop** | ✅ |
| CONSENT-07 | **关键红线**：边界（review）案例不进入普通内容生成，未成年人权益优先 | `true` | `2026-10-16T10:10:00+08:00` | granted | **granted** | stop | **stop** | ✅ |
