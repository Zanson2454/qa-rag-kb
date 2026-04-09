# Iter 012 Change Record

artifact:
  id: iter-012-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

执行 Iter-012：判断 defect `missing_expected` 高占比到底属于源模板长期噪声还是当前解析缺口，并把 warning 收录策略固化为 admission policy；本轮仍严格停留在 Phase 1 导入质量层。

## 新增/修改文件

- `docs/exec-plans/active/iter-012-defect-expected-policy-plan.md`
- `src/qa_kb_importer/importer.py`
- `src/qa_kb_importer/validation.py`
- `src/qa_kb_importer/quality.py`
- `src/qa_kb_importer/cli.py`
- `docs/knowledge/import-runbook.md`
- `docs/knowledge/examples/imported-defect-example.yaml`
- `tests/test_fixed_template_importer.py`
- `tests/test_validation_and_quality.py`
- `harness/changes/iter-012-change.md`
- `harness/evaluations/iter-012-eval.md`
- `harness/reflections/iter-012-reflection.md`
- `harness/review-contexts/iter-013-context.md`
- `orchestrator/state/task-state.json`

## 每个改动对应的 plan step

- `docs/exec-plans/active/iter-012-defect-expected-policy-plan.md`
  - 对应“先 review 上轮 change record，再生成本轮 plan”
- `tests/test_fixed_template_importer.py`
  - 对应“先写 defect expected 分类与 CLI/admission 摘要失败测试”
- `tests/test_validation_and_quality.py`
  - 对应“先写 validation admission policy 与 gate 联动失败测试”
- `src/qa_kb_importer/importer.py`
  - 对应“在 importer 中补 defect expected 分类元数据与导出摘要”
- `src/qa_kb_importer/validation.py`
  - 对应“在 warning detail 中补 source_field/source_section/admission”
- `src/qa_kb_importer/quality.py`
  - 对应“把 gate 从 semantic warning rate 调整为 blocking/admissible admission policy”
- `src/qa_kb_importer/cli.py`
  - 对应“打印 admission 维度的验收摘要”
- `docs/knowledge/import-runbook.md`
  - 对应“更新 runbook 到 admission policy 口径”
- `docs/knowledge/examples/imported-defect-example.yaml`
  - 对应“同步示例产物到最新 normalized 字段”
- `orchestrator/state/task-state.json`
  - 对应“推进当前轮次并记录下一轮决策”
- `harness/changes/iter-012-change.md` 等本轮文档
  - 对应“输出本轮完整 change / evaluation / reflection / review context”

## 风险

- 当前 `expected_missing_but_description_present` 被判为 `admissible`，这是 Phase 1 的最小策略，不代表后续检索层一定可直接接受这些记录。
- `admission_distribution` 目前按 warning detail 聚合，而 gate 仍按记录级比例判断，两个口径需要在后续文档中持续解释清楚。
- `expected` 仍未从 `缺陷描述*` 自动生成高置信文本，本轮只是先做分类和收录策略，不是完整补全。

## 未解决问题

- `expected_missing_but_description_present` 是否需要在下一轮尝试自动生成候选 `expected`，还没定稿。
- validation details 仍停留在字段名和 section 级，没有源文本片段或更细的段落偏移。
- 是否已经具备进入检索层准备工作的前提，需要结合 warning 收录策略再做一次判断。
