# Iter 013 Change Record

artifact:
  id: iter-013-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

执行 Iter-013：完成 QA KB Phase 1 的最后收口，为 importer 增加重复 source_id 检查、目标路径冲突拦截、正式错误清单结构，以及进入下一阶段前的准入标准说明。

## 新增/修改文件

- `docs/exec-plans/active/iter-013-phase1-closure-plan.md`
- `src/qa_kb_importer/importer.py`
- `src/qa_kb_importer/cli.py`
- `docs/knowledge/import-runbook.md`
- `tests/test_fixed_template_importer.py`
- `harness/changes/iter-013-change.md`
- `harness/evaluations/iter-013-eval.md`
- `harness/reflections/iter-013-reflection.md`
- `harness/review-contexts/iter-014-context.md`
- `orchestrator/state/task-state.json`

## 每个改动对应的 plan step

- `docs/exec-plans/active/iter-013-phase1-closure-plan.md`
  - 对应“先收敛 Phase 1 剩余缺口，再实现”
- `tests/test_fixed_template_importer.py`
  - 对应“先写重复 source_id / target_conflict / manifest / CLI 摘要失败测试”
- `src/qa_kb_importer/importer.py`
  - 对应“在 importer 中补重复检查、目标冲突处理、错误清单细化和 manifest 收口”
- `src/qa_kb_importer/cli.py`
  - 对应“在 CLI 输出中补 conflict 摘要”
- `docs/knowledge/import-runbook.md`
  - 对应“固化 Phase 1 准入标准、版本边界和冲突处理规则”
- `harness/changes/iter-013-change.md` 等本轮文档
  - 对应“输出本轮完整 change / evaluation / reflection / review context”
- `orchestrator/state/task-state.json`
  - 对应“推进仓库状态到 Iter-013 收口结果”

## 风险

- 当前仍固定 `version=1`，只做冲突拦截，不做自动升版；这符合 Phase 1 边界，但意味着 Phase 2 前仍需规划正式版本合并策略。
- `success_count` 与 `warning_count` 是不同口径：前者是落盘成功记录数，后者是质量标记计数，后续文档必须持续区分。
- 当前 `target_conflict` 只做“拦截并记错”，不提供自动人工复核流。

## 未解决问题

- 自动升版与版本比对仍未实现，只完成了 Phase 1 所需的冲突拦截边界。
- admissible warning 是否足够允许进入检索层准备阶段，仍需要单独定稿。
- 还没有从 `缺陷描述*` 自动生成候选 `expected`，这属于下一阶段质量收敛项。
