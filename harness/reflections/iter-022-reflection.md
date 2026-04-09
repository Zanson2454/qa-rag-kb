# Iter 022 Reflection

artifact:
  id: iter-022-reflection
  type: reflection
  stage: reviewing
  status: approved

## 本轮反思

- Iter-021 的恢复规则对小批次是有效的，但它本质上只是 3 类症状模板，不足以覆盖中等批次里更常见的标题语义。
- 中等批次剩余 warning 并不是随机噪声，而是集中在少数稳定形态：接口报错、行为期待、bundle 型问题单、以及非 defect 问句型条目。
- loop 主线这轮没有回归，说明当前系统的瓶颈已经重新回到 importer 质量层本身。

## 经验

- 对启发式恢复规则，`3 + 3` 的小批次通过只能证明“规则成立”，不能证明“规则稳定”；中等批次放大验证是必要步骤。
- 当 warning 已经能按记录形态收敛成几类时，下一轮应该先做分类驱动的最小规则扩展，而不是继续放松 gate。
- 对明显不像 defect 的记录，提前决定拒收或分流策略，比继续硬补 `expected` 更稳。

## 下一步建议

- 先为标题直带期望语义的 defect 增加更保守的 title-driven `expected` 恢复。
- 单独定义 `问题若干 / 问题集合 / 需求确认 / 布局调整` 这类 bundle 或需求式条目的准入策略。
- 再跑一次 `20 + 20` 中等批次验收，确认 warning 是否显著下降。
