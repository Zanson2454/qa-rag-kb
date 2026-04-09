# Iter 017 Change Record

artifact:
  id: iter-017-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

执行 `ruff format` 基线收敛，让自治 loop 越过第一层格式 gate，并确认新的真实阻断点。

## 新增/修改文件

- `docs/exec-plans/active/iter-017-ruff-format-baseline-plan.md`
- `tests/test_governance_assets.py`
- `harness/changes/iter-017-change.md`
- `harness/evaluations/iter-017-eval.md`
- `harness/reflections/iter-017-reflection.md`
- `harness/review-contexts/iter-018-context.md`
- `orchestrator/state/task-state.json`

## 风险

- 本轮只收敛了 `ruff format`，并没有解决 `ruff check` 当前暴露出的 `E402` 问题。
- 工作树里仍有其他未收口改动，本轮提交需要继续严格限制在 `ruff format` 基线与 Iter-017 文档上。
- 真实 loop 仍停在 fast gate，尚未进入 business gate。

## 未解决问题

- `tests/test_fixed_template_importer.py` 与 `tests/test_validation_and_quality.py` 的导入顺序仍触发 `ruff check` `E402`。
- 是否需要把旧的 `iter-015-ruff-format-baseline-plan.md` 归档或删除，当前尚未处理。
