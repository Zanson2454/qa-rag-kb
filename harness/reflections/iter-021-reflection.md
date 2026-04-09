# Iter 021 Reflection

artifact:
  id: iter-021-reflection
  type: reflection
  stage: reviewing
  status: approved

## 本轮反思

- 这轮有效的关键不是调 gate，而是把最集中的 3 条 warning 转换成可解释、可测试的导入恢复规则。
- 先做 RED，再把恢复逻辑限制在 3 类高置信症状上，避免了为了清零 warning 去扩散启发式范围。
- loop 主线当前已经不需要继续修传播链路，业务质量层也在小批次上达到了 `passed`。

## 经验

- 对结构化缺口，优先补最小恢复规则，比直接放宽 gate 更稳。
- 对启发式规则，先用当前样本固定语义，再放大样本规模做稳定性验证，是更合适的推进顺序。

## 下一步建议

- 在 `20 + 20` 中等批次上重新运行 importer 验收，确认当前候选恢复规则不是只对 `3 + 3` 生效。
- 若中等批次仍稳定，应把当前 passed 基线正式固化到 loop 主线。
