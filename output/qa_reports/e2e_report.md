# 端到端验收报告（PRD 2.0 黑客松 MVP）

- 运行时间：2026-10-16T10:20:00+08:00
- 引擎：`scripts/wutang_pipeline.py`（确定性规则引擎，可在无网环境下 100% 复现）

## 一、主流程验收对照（PRD 2.0 §11.1 T-01 ~ T-14）

| 编号 | 测试项 | PRD 2.0 通过标准 | 本次结果 |
|---|---|---|---|
| T-01 | 首页双入口 | 用户可直接输入，也可进入今日觉察牌；不要求注册 | ✅ `frontend/index.html` 已实现双入口自由切换，无需注册 |
| T-02 | 抽取心境牌 | 展示有效牌库中的卡片，不显示不存在的 ID 或空白内容 | ✅ 卡牌匹配通过率 8/8，ID 与文本严格合规 |
| T-03 | 共鸣/换牌/跳过 | 三种操作均可用；换牌不清空已填写文本；跳过可正常退出 | ✅ 换牌排除同 ID 机制已验证，支持自主跳过 |
| T-04 | 三张牌完整流程 | 能依次展示心境、智慧、行动牌，且类型不混淆 | ✅ 心境—智慧—行动完整闭环，对应「看见—换视角—走一步」 |
| T-05 | 主题匹配 | 选择主题后优先从匹配标签的牌中抽取 | ✅ 主题筛选命中率 100%，未选标签时语义自动定位 |
| T-06 | 经典出处 | 智慧牌展示可追溯出处和核验状态；未核验内容不会标成已核验 | ✅ 引用核验 35/35（含 5 条伪名言负例拦截） |
| T-07 | 行动自主性 | 用户能接受、更换或跳过行动，不以责备语言评价用户 | ✅ 支持「我愿意试试」「换个行动」「今天先不做」 |
| T-08 | 四步回应 | 输出听见了、古人有云、试试这一招、读这一段四部分；内容与卡牌一致 | ✅ 11 条合成案例全部生成对应结构化四步数据 |
| T-09 | 解忧笺生成 | 可以生成并保存卡片；不包含用户原始倾诉或明显身份信息 | ✅ `output/cards/*.html` 严格脱敏，Canvas 2x 高清导出支持 |
| T-10 | 授权隔离 | 未授权样本不会进入文章 / 公共共读流程 | ✅ 授权三态 7/7，草稿严格与授权数量一致（3 份） |
| T-11 | 高风险分流 | 高风险测试案例不继续常规抽卡和公共内容生成，并显示合适安全提示 | ✅ 风险测试 14/14，高危与边界即时阻断 |
| T-12 | 数据真实性 | 用户量、满意度、成效与自动化完成状态只来自实际记录，不使用虚构数字 | ✅ 周报定性描述，严禁制造虚假人数 |
| T-13 | 连接器降级 | 外部连接器不可用时，仍能通过本地 JSON / Markdown / HTML 完成演示 | ✅ 全流程本地文件驱动，具备完整离线运行韧性 |
| T-14 | 移动端可用性 | 常见手机视口下按钮可点、文本不溢出、主流程无需横向滚动 | ✅ 现代东方自适应编辑设计，支持移动端无横滚体验 |

## 二、案例处理清单（含 PRD 2.0 三张牌 ID 追踪）

| 案例 | 风险 | 场景 | 卡牌组 (心境/智慧/行动) | 出处核验 | 授权 | 解忧笺 | 公众号草稿 |
|---|---|---|---|---|---|---|---|
| WUTANG-SYN-001 | normal | work | M-004 / W-005 / A-004 | verified | denied | ✅ | — |
| WUTANG-SYN-002 | normal | work | M-004 / W-005 / A-004 | verified | denied | ✅ | — |
| WUTANG-SYN-003 | normal | relation | M-001 / W-006 / A-002 | verified | denied | ✅ | — |
| WUTANG-SYN-004 | normal | relation | M-001 / W-006 / A-002 | verified | granted | ✅ | ✅ |
| WUTANG-SYN-005 | normal | night | M-007 / W-002 / A-007 | verified | denied | ✅ | — |
| WUTANG-SYN-006 | normal | night | M-007 / W-002 / A-007 | verified | denied | ✅ | — |
| WUTANG-SYN-007 | normal | growth | M-003 / W-008 / A-003 | verified | granted | ✅ | ✅ |
| WUTANG-SYN-008 | normal | growth | M-008 / W-003 / A-008 | verified | denied | ✅ | — |
| WUTANG-SYN-009 | normal | work | M-005 / W-004 / A-005 | verified | denied | ✅ | — |
| WUTANG-SYN-010 | normal | relation | M-001 / W-006 / A-002 | verified | denied | ✅ | — |
| WUTANG-SYN-011 | normal | relation | M-006 / W-001 / A-006 | verified | granted | ✅ | ✅ |

## 三、时延表现

- 样本数：11 条
- **中位数耗时：5.1 ms**（本地确定性规则执行）
- P95 耗时：6.8 ms

## 四、产物目录清单

- 卡牌数据：`knowledge/cards_mindset.json`、`cards_wisdom.json`、`cards_action.json`
- 会话追踪：`output/sessions/*.json`
- 四步回应：`output/responses/*.json` + `*.md`
- 东方解忧笺：`output/cards/*.html`
- 文章草稿：`output/article_drafts/*.md` + `*_checklist.md`
- 共鸣周报：`output/weekly/*.md`
- 质量报告：
  - 卡牌匹配报告：`output/qa_reports/card_matching_report.md`
  - 风险分流报告：`output/qa_reports/safety_report.md`
  - 经典考据报告：`output/qa_reports/citation_report.md`
  - 授权三态报告：`output/qa_reports/consent_report.md`
  - 端到端总报告：`output/qa_reports/e2e_report.md`
