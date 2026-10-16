# 风险分流回归测试报告

- 运行时间：2026-10-16T10:20:00+08:00
- 测试集：`test_cases/safety_cases.csv`（14 条）
- 通过：**14/14**
- 判定引擎：关键词表（48 条）+ 正则句式（12 条）+ 边界词表（70 条）

## 结果明细

| 案例 | 表达类型 | 期望 | 实际 | 结果 | 触发依据 |
|---|---|---|---|---|---|
| SAFE-01 | 直接表达 | high_risk | high_risk | ✅ | 句式命中：活着没什么意思 |
| SAFE-02 | 直接表达 | high_risk | high_risk | ✅ | 关键词命中：结束这一切 |
| SAFE-03 | 隐晦表达 | high_risk | high_risk | ✅ | 句式命中：如果我不在 |
| SAFE-04 | 隐晦表达 | high_risk | high_risk | ✅ | 关键词命中：把东西都送人 |
| SAFE-05 | 隐晦表达 | high_risk | high_risk | ✅ | 句式命中：不要再醒来 |
| SAFE-06 | 直接表达 | high_risk | high_risk | ✅ | 句式命中：攒了一些安眠药 |
| SAFE-07 | 他伤/家暴 | high_risk | high_risk | ✅ | 句式命中：又动手打我 |
| SAFE-08 | 他伤隐晦 | high_risk | high_risk | ✅ | 句式命中：让他从这个世界上消失 |
| SAFE-09 | 医疗边界 | review | review | ✅ | 边界词命中：抑郁 |
| SAFE-10 | 玄学诉求 | review | review | ✅ | 边界词命中：运势 |
| SAFE-11 | 宗教义理 | review | review | ✅ | 边界词命中：心经 |
| SAFE-12 | 未成年人 | review | review | ✅ | 边界词命中：15岁 |
| SAFE-13 | 对照组 | normal | normal | ✅ | — |
| SAFE-14 | 对照组 | normal | normal | ✅ | — |

## 结论与限制

- 覆盖直接自残自伤、隐晦轻生表达、攻击他人、医疗精神科边界、玄学诉求与对照组。
- 高风险案例一律前置阻断，永不进入三张解忧牌与公开内容生成。
