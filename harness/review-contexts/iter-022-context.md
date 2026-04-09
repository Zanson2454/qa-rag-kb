# Iter 022 Review Context

artifact:
  id: iter-022-context
  type: review-context
  stage: reviewing
  status: approved

## 当前已完成内容

- Iter-021 已为 defect 缺失 `expected` 增加最小候选恢复。
- 小批次正式回归测试已通过：
  - `tests/test_fixed_template_importer.py`
  - `tests/test_validation_and_quality.py`
- loop 相关回归测试已通过：
  - `tests/test_orchestrator_v0.py`
  - `tests/test_orchestrator_loop_runner.py`
- 真实 importer 小批次结果已变为：
  - `gate=passed`
  - `warnings=0`
  - `warning_code_distribution: {}`
- 真实 loop 已返回：
  - `loop iteration=21 ok=true stop_reason=none`

## 本轮关键结论

- 当前 `warnings=3` 已被消除。
- loop 使用的小批次 importer 基线已经达到 `passed`。
- 当前剩余问题不在 gate 传播，也不在小批次 warning，而在恢复规则放大到更大样本后的稳定性。

## 未解决问题

- 尚未重新验证 `20 + 20` 中等批次下的稳定性。
- 尚未决定是否要保留 `missing_expected_section` 作为并行原始缺口标记。

## 下一轮优先事项

- 重新运行中等批次 importer 验收。
- 判断当前候选恢复规则是否可稳定推广。
- 若稳定，则把新的 passed importer 基线固化给 loop 主线。
