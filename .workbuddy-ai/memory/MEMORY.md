# 悟堂项目 —— 长期约定

## 项目定位

`D:/BaiduSyncdisk/02-DEV/悟堂` —— 悟堂·东方解忧处。
面向成年人的日常情绪整理工具 + 面向公益内容主理人的 WorkBuddy 内容工作流引擎。
赛事：ACC 2026 × WorkBuddy 超级个体极限挑战赛。
主文档：`PRD.md`（= `DOC/悟堂_项目开发PRD.md` 的副本）。

## 目录约定

```
knowledge/     资料库 A（经典语料 500 条）+ B（品牌与安全规则）+ 原始素材 *_raw.txt
.workbuddy-ai/skills/   4 个核心 Skill（项目级）
frontend/      index.html 为构建产物；改样式/逻辑要改 _template.html 再跑 build_frontend.py
scripts/       build_knowledge.py → build_frontend.py → wutang_pipeline.py（按此顺序）
               gen_part1..7.py + knowledge_corpus/  语料扩充流水线（生成 500 条）
               make_sage_avatars.py  先贤头像生成
test_cases/    四份 CSV（synthetic_normal / citation / safety / consent）
output/        responses / cards / article_drafts / qa_reports / weekly
inbox/         待处理提问入口（自动化工作流读取）
mcp/           wutang-kb-server.js 本地 MCP 连接器
docs/          演示脚本 + 截图
```

**重要**：`frontend/index.html` 是**生成物**，不要直接改；改 `frontend/_template.html` 后重跑 `build_frontend.py`。
数据通过 `<script id="wutang-data" type="application/json">` 内联（构建后约 750KB），页面用 `JSON.parse` 读取。
前端是**双模式单页**：用户端（`clientArea`，四步回应 + 解忧笺）+ 主理人端（studio，概览 / 复核 / 流水线）。

## 不可妥协的规则（写死在 safety_rules.md，优先级最高）

1. **不编造经典原文、作者、篇章、典故。** 检索不到就写「未找到可信出处」。
2. **三级核验状态**：`verified` 可作直接引语 / `needs_review` 须标「辑录·待复核」/ `not_found` 禁止引用。
3. **未授权不进入公开内容流程**；`consent_for_public_draft` 字段缺失 = 未授权。
4. **同意分享个人卡片 ≠ 同意公开原始问题。**
5. **公开内容一律「待主理人审核」，不自动发布。**
6. **高风险案例永不进入公开内容生成**，即使已授权。
   **边界案例（`review`：涉未成年人 / 医疗用药 / 精神科 / 玄学诉求）同样不进入，授权不改变结论。**
7. **不宣称 100% 识别危机、不宣称引文 100% 准确。**
8. **不生成伪造用户数量**；样本少时用定性描述。**低于披露阈值时任何计数都是泄露**（连「出现于 1 条」都不行）。
9. **卡片不含原始倾诉与任何 PII。**

## 数据纪律

- 每条引用必须携带 `source_id`，可回溯到 `knowledge/source_index.md`。
- 新增语料必须填全部 15 个字段，`verifier` 不得为空，未核验不得标 `verified`。
- 每次订正出处，必须在 `source_index.md` 的「订正记录」追加一行。
- 区分「事实 / 推断 / 建议」，不混写。

## 已知的技术取舍

- 前端与 `wutang_pipeline.py` 是**确定性规则引擎**，不调大模型 —— 用于离线降级、回归测试、
  「同一输入产出同一结果」的可验证性。完整版由 WorkBuddy 专家团生成。
- 语料规模：**500 条**（verified 483 / needs_review 7 / not_found 10），风险词 48 + 复核词 70 + 正则 12 条。
- 风险分流是**关键词 + 正则双轨兜底**，不是语义理解。正式部署必须叠加模型判断 + 人工复核测试集。
- 修改风险词表后，**必须重跑 `wutang_pipeline.py`** 并检查 `output/qa_reports/safety_report.md` 的通过数。

## 一键运行（完整链路）

```bash
PY="C:/Users/ausda/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
"$PY" scripts/build_knowledge.py   # 500 条语料 → classics.csv/json
"$PY" scripts/build_frontend.py    # 数据内联 → index.html（约 750KB）
"$PY" scripts/wutang_pipeline.py   # 四步回归：风险 / 引用 / 授权 / 案例 → output/
```

当前基线（2026-10-16）：风险 **14/14** ｜ 引用 **35/35** ｜ 授权 **7/7** ｜ 案例 11 条（草稿 3 份）。
**任一项不是全绿就说明改动引入了回归。**

## 专家团

`wutang-relief`（悟堂解忧团），位置 `~/.workbuddy-ai/plugins/marketplaces/my-experts/plugins/`。
1 主理人（常明川·解忧流程导演）+ 5 成员（严守拙/闻心语/章有据/步小成/舒成锦）。
**两个叫停点**：风险闸口（Phase 1）、授权闸口（Phase 7）—— 这是团队拆分存在的理由。
修改后必须重跑 `validate_expert.py` + `register_expert.py`。
头像为本地 Pillow 生成的占位图；如需 AI 头像用 ImageGen 逐张替换（按张计费，先问辉哥）。
