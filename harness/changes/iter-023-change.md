# Iter 023 Change Record

artifact:
  id: iter-023-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

作为最后 1 轮 importer warning closure，只补最窄的 title-driven `expected` 恢复和非 defect / bundle 型条目分类，然后正式停止 Phase 1 warning 调优。

## 新增/修改文件

- `docs/exec-plans/active/iter-023-one-round-warning-closure-plan.md`
- `src/qa_kb_importer/importer.py`
- `src/qa_kb_importer/validation.py`
- `tests/test_fixed_template_importer.py`
- `tests/test_validation_and_quality.py`
- `harness/changes/iter-023-change.md`
- `harness/evaluations/iter-023-eval.md`
- `harness/reflections/iter-023-reflection.md`
- `harness/review-contexts/iter-024-context.md`
- `orchestrator/state/task-state.json`

## 改动结果

- 在 `importer.py` 中新增最窄的 title-driven `expected` 恢复，仅覆盖：
  - `没保存上`
  - `未显示全`
  - `没有回显`
  - `报 500/404`
  - `过账后才允许`
- 在 `validation.py` 中新增两类专用 warning code：
  - `question_like_record`：blocking
  - `bundle_like_record`：admissible
- 通过补充防误判测试，把 special classification 收紧到 title / content_text 范围，不再因为 steps-only 文字触发误判。
- 让问句型和 bundle 型记录从普通 `missing_expected` 中分离，不再继续堆在一个大类里。
- 新增 RED/GREEN 测试覆盖 title-driven 恢复、问句型分类、bundle 型分类和 report 聚合。
- 按 stop rule 完成最后一次真实 `20 + 20` 验收：
  - `gate=warning`
  - `warnings=7`
  - `admissible_warnings=6`
  - `blocking_warnings=1`
  - `conflicts=0`
- 相比 Iter-022：
  - `warnings: 18 -> 7`
  - `missing_expected: 17 -> 2`
  - 主要剩余 warning 已变成显式分类：
    - `bundle_like_record: 3`
    - `question_like_record: 1`
    - `testcase_steps_too_short: 1`

## 风险

- 中等批次仍是 `gate=warning`，说明 importer 质量层还有已知限制。
- 本轮故意没有继续扩更多标题模式，也没有继续细化剩余 `missing_expected`，避免再次进入无上限优化。

## 未解决问题

- `DEF-822065` 这类 `bug若干` 记录仍落在普通 `missing_expected`。
- `DEF-823636` 这类“控制台报错”标题仍未进入本轮允许的 title-driven 恢复范围。
- `TC-1735084` 仍保留 `testcase_steps_too_short`。
- 按本轮 stop rule，这些都作为已知限制保留，不再继续 Phase 1 warning 调优。
