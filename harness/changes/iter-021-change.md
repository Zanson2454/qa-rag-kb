# Iter 021 Change Record

artifact:
  id: iter-021-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

为缺失结构化 `expected` 的 defect 增加最小候选补全能力，收敛当前 `warnings=3` 的 importer 质量基线。

## 新增/修改文件

- `docs/exec-plans/active/iter-021-expected-candidate-recovery-plan.md`
- `src/qa_kb_importer/importer.py`
- `tests/test_fixed_template_importer.py`
- `tests/test_validation_and_quality.py`
- `harness/changes/iter-021-change.md`
- `harness/evaluations/iter-021-eval.md`
- `harness/reflections/iter-021-reflection.md`
- `harness/review-contexts/iter-022-context.md`
- `orchestrator/state/task-state.json`

## 改动结果

- 在 `importer.py` 中新增 defect `expected` 候选恢复逻辑。
- 仅覆盖 3 类高置信症状：
  - `失败`
  - `不一致`
  - `报错...为空`
- 恢复成功时显式写入：
  - `expected_resolution = expected_generated_from_symptom`
  - `expected_source_section`
  - `generated_expected_candidate`
- 新增正式回归测试，覆盖症状恢复、validation 收敛和 batch report 收敛。
- 真实 importer 小批次结果已从 `gate=warning warnings=3` 收敛到 `gate=passed warnings=0`。

## 风险

- 当前恢复仍是关键字启发式，若后续原始描述出现更复杂语义，可能误命中或漏命中。
- 本轮只验证了当前 loop 使用的 `3 defect + 3 testcase` 样本规模，尚未重新验证更大样本下的稳定性。

## 未解决问题

- 还没有确认这套候选恢复在 `20 + 20` 中等批次下是否同样稳定。
- 还没有决定是否需要把 `missing_expected_section` 与 `generated_expected_candidate` 同时保留为双重痕迹。
