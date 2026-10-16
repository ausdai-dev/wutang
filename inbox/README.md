# inbox/ —— 待处理提问入口

把待处理的提问放到这里（一条一个 `.json` 或 `.md` 文件），「今日悟堂解忧与成文工作流」会读取本目录。

## JSON 格式（推荐）

```json
{
  "case_id": "WUTANG-20261016-001",
  "created_at": "2026-10-16T20:00:00+08:00",
  "scenario_tag": "work",
  "user_text": "……",
  "risk_status": "normal",
  "consent_for_public_draft": false,
  "consent_timestamp": null,
  "processing_status": "received",
  "retention_note": "仅用于当前处理；未经授权不进入公开内容库"
}
```

## 重要

- **`consent_for_public_draft` 为 `false` 或缺失时，该案例不得进入文章草稿流程。**
- 不要在此目录存放未经授权的真实隐私文本。
- 演示结束后请清理本目录与 `output/` 中的临时文件。
- 若本目录为空，工作流会跳过并如实说明「无新提问」，不会自行编造案例。
