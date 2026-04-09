# Iter 014 Change Record

artifact:
  id: iter-014-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

实现 Iter-014：为状态文件增加 canonical plan pointer，消除历史多 plan 并存导致的 `plan_conflict`，让自治 loop 可以基于唯一主线继续推进。

## 新增/修改文件

- `docs/exec-plans/active/iter-014-plan-pointer-alignment-plan.md`
- `orchestrator/validation.py`
- `orchestrator/run_loop.py`
- `orchestrator/README.md`
- `orchestrator/state/task-state.json`
- `tests/test_orchestrator_loop_runner.py`
- `tests/test_orchestrator_v0.py`
- `harness/changes/iter-014-change.md`
- `harness/evaluations/iter-014-eval.md`
- `harness/reflections/iter-014-reflection.md`
- `harness/review-contexts/iter-015-context.md`

## 每个改动对应的 plan step

- `tests/test_orchestrator_loop_runner.py`
  - 对应“先写 current_plan 覆盖多 plan 冲突、缺失、错配的失败测试”
- `tests/test_orchestrator_v0.py`
  - 对应“补 current_plan 结构校验回归测试”
- `orchestrator/validation.py`
  - 对应“在状态校验中补 current_plan 结构约束”
- `orchestrator/run_loop.py`
  - 对应“让 loop 优先使用 canonical plan，并把错配转成结构化 stop reason”
- `orchestrator/README.md`
  - 对应“补充 canonical plan 的使用说明”
- `orchestrator/state/task-state.json`
  - 对应“写入当前 iteration 的 canonical plan，并推进本轮状态”
- `harness/changes/iter-014-change.md` 等本轮文档
  - 对应“补齐本轮 evaluation / reflection / review context”

## 风险

- 当前只是消除了 `plan_conflict`，并没有自动修复后续 fast gate 问题。
- `current_plan` 依赖状态文件维护正确性，如果后续更新不及时，仍可能导致 loop 阻断。
- 当前 loop 还没有自动归档旧 plan 的能力，历史 plan 仍会继续存在。

## 未解决问题

- 真实 loop 现在卡在 `fast_gate_failed`，下一轮需要决定是先收敛格式基线还是参数化 fast gates。
- 还没有实现对旧 plan 的归档或失效标记机制。
- `current_plan` 目前只支持单一 canonical path，还没有扩展到多计划协同场景。
