# Iter 019 Change Record

artifact:
  id: iter-019-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

对齐自治 loop 与 importer CLI 的 business gate 失败语义，让 `gate=failed` 通过退出码传播给 loop，同时为 loop 使用独立 `knowledge_root`，避免重跑时污染正式 `docs/knowledge`。

## 新增/修改文件

- `docs/exec-plans/active/iter-019-business-gate-semantics-plan.md`
- `src/qa_kb_importer/cli.py`
- `orchestrator/run_loop.py`
- `tests/test_fixed_template_importer.py`
- `tests/test_orchestrator_loop_runner.py`
- `harness/changes/iter-019-change.md`
- `harness/evaluations/iter-019-eval.md`
- `harness/reflections/iter-019-reflection.md`
- `harness/review-contexts/iter-020-context.md`
- `orchestrator/state/task-state.json`

## 风险

- loop 现在依赖 CLI 退出码作为 business gate 控制信号，后续如果 CLI 语义再变，需要同步维护测试。
- 独立 `knowledge_root` 解决了重跑冲突，但会让 loop 结果与正式 `docs/knowledge` 目录分离，后续需要明确哪些路径是“验收沙箱”，哪些是“正式知识库”。
- 当前 business gate 仍是 `gate=warning`，并没有消除 importer 质量层 warning 本身。

## 未解决问题

- 还没有对当前 `gate=warning warnings=3` 的具体来源做进一步分析。
- 还没决定 `warning` 是否已经是可接受基线，还是需要继续压低 warning。
