# Iter 023 Review Context

artifact:
  id: iter-023-context
  type: review-context
  stage: reviewing
  status: approved

## 当前已完成内容

- Iter-021 已在小批次上通过最小 `expected` 候选恢复，把 importer 基线收敛到 `gate=passed warnings=0`。
- Iter-022 已完成 `20 defect + 20 testcase` 中等批次验收。
- importer 与 loop 回归测试仍通过：
  - `tests/test_fixed_template_importer.py`
  - `tests/test_validation_and_quality.py`
  - `tests/test_orchestrator_v0.py`
  - `tests/test_orchestrator_loop_runner.py`
- 真实 loop 仍返回：
  - `loop iteration=22 ok=true stop_reason=none`

## 本轮关键结论

- 当前 passed importer 基线还不能直接外推到中等批次。
- 中等批次结果为：
  - `gate=warning`
  - `warnings=18`
  - `admissible_warnings=17`
  - `blocking_warnings=1`
  - `conflicts=0`
- warning 已经能定位到几类稳定形态：
  - 标题直带期望语义但未恢复
  - `问题若干 / 问题集合 / 需要产品确认 / 布局调整` 这类 bundle 或需求式条目
  - 既缺 `expected` 又缺 `actual` 的问句型记录

## 未解决问题

- 还没有 title-driven `expected` 恢复规则。
- 还没有 bundle / 需求式 / 问句型记录的准入策略。
- 还没有验证修复后中等批次 warning 是否会明显下降。

## 下一轮优先事项

- 先按剩余 warning 的标题/描述形态做分类。
- 优先补最窄的 title-driven `expected` 恢复规则。
- 明确 `DEF-824272` 这类问句型记录是否应阻断拒收。
