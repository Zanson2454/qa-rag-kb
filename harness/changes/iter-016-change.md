# Iter 016 Change Record

artifact:
  id: iter-016-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

将当前仓库主线从 Iter-015 的治理/skill 主题正式切回 `ruff loop` 收敛主题，并把状态文件与 harness 文档对齐到下一轮可继续执行 `ruff format` 基线计划的状态。

## 新增/修改文件

- `docs/exec-plans/active/iter-016-ruff-loop-mainline-switch-plan.md`
- `harness/changes/iter-016-change.md`
- `harness/evaluations/iter-016-eval.md`
- `harness/reflections/iter-016-reflection.md`
- `harness/review-contexts/iter-017-context.md`
- `orchestrator/state/task-state.json`

## 风险

- 本轮只完成主线切换，不代表 `ruff loop` 的格式基线问题已经解决。
- 既有 `iter-015-ruff-format-baseline-plan.md` 仍沿用旧编号，执行时需要明确它是“待执行计划”，不是当前 iteration 编号本身。
- 若后续又出现并行主线覆盖 `task-state.json`，仍会再次引入上下文漂移风险。

## 未解决问题

- `ruff format --check .` 的红灯范围还没有在本轮重新验证。
- 是否需要在后续把历史 `ruff loop` 计划重编为新的 iteration 编号，当前暂未处理。
