# Iter 012 Reflection

artifact:
  id: iter-012-reflection
  type: reflection
  stage: reviewing
  status: approved

## 本轮最重要的发现

- `missing_expected` 不能简单等价于“阻断质量缺陷”，至少在当前 defect 样本里，大多数都属于“缺少结构化段落，但描述仍存在”的可接受噪声。
- 一旦把 warning 分为 `admissible` 和 `blocking`，中等批次 gate 就更接近真实样本质量，而不是被单一 warning code 人为放大。
- runbook、CLI 和 report 必须使用同一套 admission 口径，否则同一批次会出现“报告说 warning，人工理解成 failed”的解释偏差。

## 当前策略仍然保守的地方

- `expected_missing_but_description_present` 现在只是被允许收录，没有尝试自动补出 `expected`。
- `missing_actual` 仍然保持 `blocking`，这在当前 Phase 1 是合理的，但后续也许需要更细分类。
- gate 仍然按记录级比例判断，不是按 warning detail 数量判断，这一点需要继续在文档里讲清楚。

## 下一轮最该优先做什么

- 判断是否要从 `缺陷描述*` 中生成候选 `expected`，把部分 admissible warning 进一步收敛。
- 明确“warning=admissible 时是否允许进入后续检索层准备工作”的正式准入标准。
- 如果准入标准已稳定，再评估是否进入检索层前置建设。
