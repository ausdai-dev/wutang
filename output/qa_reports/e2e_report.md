# 端到端验收报告（MVP）

- 运行时间：2026-10-16T10:20:00+08:00
- 引擎：`scripts/wutang_pipeline.py`（确定性规则引擎，不调用大模型，可离线复现）

## 一、验收点对照（PRD 9.1）

| 编号 | 验收点 | 通过标准 | 本次结果 |
|---|---|---|---|
| A-01 | 端到端流程 | 输入一条测试问题，可得到结构化回应、质量记录和可查看的输出文件 | ✅ 见 `output/responses/`、`output/qa_reports/` |
| A-02 | 入口易用性 | 四个场景标签清晰；无需注册即可提交 | ✅ `frontend/index.html`（离线单文件，已浏览器实测） |
| A-03 | 四步结构 | 普通问题完整输出四个部分，文字简短无明显说教感 | ✅ 11 条合成案例全部四段齐全 |
| A-04 | 来源核验 | verified 引用可在知识库中找到；未命中不编造 | ✅ 引用核验 35/35（含 5 条负例） |
| A-05 | 微行动 | 每个普通案例只推荐一个低门槛主要行动 | ✅ 每案 1 个主行动 + 3–4 步 |
| A-06 | 隐私权限 | 未授权案例不进入公开文章；输出无原始倾诉泄露 | ✅ 授权三态 7/7，草稿一致性 通过 |
| A-07 | 风险分流 | 固定高风险测试集全部按预期转入安全路径 | ✅ 14/14（详见 safety_report.md） |
| A-08 | 分享卡片 | 至少生成一张可在浏览器打开或保存的解忧笺，不含私密信息 | ✅ `output/cards/*.html`（11 张，已浏览器实测） |
| A-09 | 内容草稿 | 对已授权案例生成文章草稿和审核清单，保持待审核 | ✅ 3 份草稿 + 等量审核清单 |
| A-10 | WorkBuddy 能力 | 展示专家角色 / Skills / 资料库 / 连接器 / 可重复工作流 | ✅ 专家团 + 4 Skill + 3 资料库 + 连接器 + 自动化（见 README） |
| A-11 | 真实验证 | 有真实测试记录和反馈原文 | ❌ **未完成**：全部为合成测试案例，**无真实用户测试记录** |
| A-12 | 故障降级 | 连接器不可用时仍可通过本地文件完成演示 | ✅ 本引擎全程本地文件，无外部依赖 |

## 二、案例处理清单

| 案例 | 风险 | 场景 | 来源编号 | 核验 | 授权 | 卡片 | 文章草稿 |
|---|---|---|---|---|---|---|---|
| WUTANG-SYN-001 | normal | work | CLASSIC-394 | verified | denied | ✅ | — |
| WUTANG-SYN-002 | normal | work | CLASSIC-100 | verified | denied | ✅ | — |
| WUTANG-SYN-003 | normal | relation | CLASSIC-082 | verified | denied | ✅ | — |
| WUTANG-SYN-004 | normal | relation | CLASSIC-206 | verified | granted | ✅ | ✅ |
| WUTANG-SYN-005 | normal | night | CLASSIC-425 | verified | denied | ✅ | — |
| WUTANG-SYN-006 | normal | night | CLASSIC-165 | verified | denied | ✅ | — |
| WUTANG-SYN-007 | normal | growth | CLASSIC-182 | verified | granted | ✅ | ✅ |
| WUTANG-SYN-008 | normal | growth | CLASSIC-023 | verified | denied | ✅ | — |
| WUTANG-SYN-009 | normal | work | CLASSIC-210 | verified | denied | ✅ | — |
| WUTANG-SYN-010 | normal | relation | CLASSIC-344 | verified | denied | ✅ | — |
| WUTANG-SYN-011 | normal | relation | CLASSIC-239 | verified | granted | ✅ | ✅ |

统计：{'normal': 11}

## 三、授权一致性核对（A-06 关键项）

| 项 | 值 |
|---|---|
| 通过授权闸口的案例数 | 3 |
| `article_drafts/` 下实际草稿数 | 3 |
| 一致性 | ✅ 相等 —— 授权闸口有效 |

> 未授权案例**不会**出现在 `article_drafts/` 中。这条核对是防止"代码写了闸口但实际没关"的兜底检查。

## 四、时延记录（PRD 9.2）

- 样本：11 条（逐案例计时，含风险分流 + 场景定位 + 经典检索 + 四步组装 + 卡片生成）
- **中位数：4.4 ms**
- P95：7.8 ms

| 案例 | 耗时 (ms) |
|---|---|
| WUTANG-SYN-001 | 4.4 |
| WUTANG-SYN-002 | 3.3 |
| WUTANG-SYN-003 | 4.2 |
| WUTANG-SYN-004 | 5.9 |
| WUTANG-SYN-005 | 3.8 |
| WUTANG-SYN-006 | 3.4 |
| WUTANG-SYN-007 | 5.6 |
| WUTANG-SYN-008 | 4.9 |
| WUTANG-SYN-009 | 4.6 |
| WUTANG-SYN-010 | 3.5 |
| WUTANG-SYN-011 | 7.8 |

> ⚠️ **限制**：这是**本地规则运算**的耗时，**不构成大模型生成时延的参考**。
> 真实端到端时延（含模型推理）**未实测**，因此**不宣传「30 秒必达」**。

## 五、F-08 每周共鸣主题周报

- 进入统计的授权案例：**3 条**
- 输出：`output/weekly/2026-W42_共鸣主题周报.md`
- 样本低于披露阈值，已按 PRD F-08 要求**改用定性描述、不显示精确人数**。
- 未授权原始提问**未纳入统计**，也未以汇总/改写/匿名化方式绕过授权。

## 六、产物清单

- 四步回应：`output/responses/*.json` + `*.md`
- 东方解忧笺：`output/cards/*.html`
- 公众号草稿：`output/article_drafts/*.md`（仅授权案例）
- 审核清单：`output/article_drafts/*_checklist.md`
- 周报：`output/weekly/2026-W42_共鸣主题周报.md`
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
