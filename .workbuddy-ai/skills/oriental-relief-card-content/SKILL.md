---
name: oriental-relief-card-content
description: 生成东方解忧笺（可保存的国风卡片），以及经授权案例的公众号文章草稿。当需要把四步回应转成视觉卡片、或为已授权案例生成公众号标题与正文时加载。输入已核验的四步回应、经典来源、授权与脱敏结果、品牌文风手册；输出卡片 HTML、标题候选、文章正文、互动问题、待审核清单。
---

# Skill 4 · 解忧笺与文章草稿生成（oriental-relief-card-content）

> 本 Skill 有**两个模式**，用途不同、权限不同，不可混用。

## 模式 A：东方解忧笺（F-04，L2 权限）

### 触发

任何一次正常的四步回应完成后，均可生成解忧笺。**无需公开内容授权。**

### 必含内容（至少）

1. 一个情绪 / 场景主题词；
2. 一句**已核验出处**的经典原文，或**明确标为「现代转述」**的短句；
3. 一句简洁的现代解释；
4. 一个 5 分钟微行动；
5. 「悟堂·东方解忧处」品牌标识。

### 禁止包含（硬性）

- ❌ 用户原始倾诉
- ❌ 姓名 / 公司 / 具体地点 / 可识别关系细节
- ❌ 未脱敏案例摘要
- ❌ 危机内容
- ❌ 系统内部提示（source_id、verification_status、prompt 等）

> **卡片分享 ≠ 授权将原始问题用于公众号内容。** 两种权限必须分开。

### 视觉规范

| 项 | 值 |
|---|---|
| 底色 | 暖白 `#FBF7F0` |
| 点缀 | 深红棕 `#8C3A2B` |
| 正文 | 低饱和墨色 `#2B2724` |
| 排版 | 简洁宋式；标题衬线；留白充足 |

**原则：不为了装饰牺牲文字可读性。**

### 输出

`output/cards/<case_id>.html` —— 单文件、可离线打开、可打印保存为图片。

## 模式 B：公众号文章草稿（F-07，L3 权限）

### 触发（前置条件，全部满足才可执行）

1. `privacy-consent-review` 返回 `allowed_next_step` ≠ `stop`；
2. `consent_for_public_draft === true` 且有 `consent_timestamp`；
3. `risk_status === normal`（`high_risk` 与 `review` 均不进入公开内容生成）。

**任一不满足 → 只处理为用户本人可见的个人回应和分享卡片，禁止进入案例文章或共读周报。**

### 执行步骤

1. **去标识化**：对姓名、地名、单位、时间、职业身份、亲属关系和独特事件等识别信息做处理。
2. **生成脱敏检查清单**：列出仍可能导致识别的细节。
3. **改写为面向公众的主题文章**：把个案转为公共议题。
   - ⚠️ **不能只靠替换人名来认定脱敏完成。**
4. **附可核验的经典出处**：标明原文、现代解释、编辑者需复核的位置。
5. **生成 3 个标题候选 + 文章正文 + 文末互动问题 + 配图建议**。
6. **状态标记为「待主理人审核」，不自动公开发布。**

### 输出

- `output/article_drafts/<case_id>.md` —— 文章草稿
- `output/article_drafts/<case_id>_checklist.md` —— 脱敏与审核清单

## 输出结构

```json
{
  "case_id": "WUTANG-TEST-001",
  "mode": "card | article",
  "card": {
    "theme": "情绪/场景主题词",
    "quote": "已核验原文或现代转述",
    "quote_source": "书名·篇章 或 「现代转述」",
    "quote_status": "verified | needs_review | modern_paraphrase",
    "explanation": "一句现代解释",
    "micro_action": "今晚 5 分钟微行动（一句话版）",
    "brand": "悟堂·东方解忧处",
    "html_path": "output/cards/WUTANG-TEST-001.html"
  },
  "article": {
    "title_candidates": ["标题一", "标题二", "标题三"],
    "body_markdown": "文章正文",
    "interactive_question": "文末互动问题",
    "image_suggestions": ["配图建议"],
    "citation_block": "可核验的经典出处",
    "review_status": "待主理人审核"
  }
}
```

## 铁律

| 编号 | 规则 |
|---|---|
| R1 | 卡片不显示原始倾诉，不显示任何 PII。 |
| R2 | 文章只使用授权材料。 |
| R3 | **不产生伪造用户数量**。样本少时用定性描述，不显示精确人数。 |
| R4 | 输出**仅为草稿**，一律「待主理人审核」。 |
| R5 | 不自动发布，不调用任何发布接口。 |
| R6 | 卡片上的原文必须带核验状态；`needs_review` 的必须标为「辑录」，`not_found` 的必须标为「现代转述」。 |
| R7 | 若使用公众号二维码，须由主理人提供合法可用素材，不得自行生成。 |

## 参考资源

- `knowledge/brand_tone.md` §5 §6 —— 卡片视觉规范、授权文案
- `knowledge/safety_rules.md` §3 §5 —— 授权分层、公开内容审核清单
- `frontend/assets/wutang-data.json` —— 品牌文案与微行动库
