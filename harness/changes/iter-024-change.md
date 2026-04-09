# Iter 024 Change Record

artifact:
  id: iter-024-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

在 Iter-023 签收后，停止继续 Phase 1 warning 调优，正式把主线切到知识库下一阶段的 retrieval-readiness planning，并定义一个有明确封顶边界的 Iter-024 执行计划。

## 新增/修改文件

- `docs/exec-plans/active/iter-024-retrieval-readiness-plan.md`
- `harness/changes/iter-024-change.md`
- `harness/evaluations/iter-024-eval.md`
- `harness/reflections/iter-024-reflection.md`
- `harness/review-contexts/iter-025-context.md`
- `orchestrator/state/task-state.json`

## 改动结果

- 明确下一阶段不直接做 embedding / vector DB / retriever，而先做 retrieval-readiness 层。
- 将下一阶段范围收敛为 4 个正式产物：
  - retrieval chunk schema
  - deterministic corpus export
  - seed eval set
  - retrieval handoff README / runbook
- 将 `task-state.json` 对齐到 Iter-024 planning 完成后的主线状态。
- 在下一轮上下文中明确：
  - Phase 1 保持完成状态
  - ruff loop v0 保持闭环可用
  - 后续不再继续 Phase 1 warning 调优

## 风险

- 如果下一轮直接跳到 retriever 或 embedding，会再次把主线拉回不可控的大范围实现。
- chunk 粒度过细或过粗都可能影响后续检索质量，因此需要先通过 deterministic export 固定接口。
- 本轮只完成 planning，不代表 retrieval-prep 已经实现。

## 未解决问题

- retrieval chunk 的最终粒度是否需要在第一次真实 export 后再微调，当前仍待验证。
- seed eval set 的 query 数量和覆盖面还没有落盘。
- 是否要把 retrieval export 纳入 loop business gate，当前暂未决定。
