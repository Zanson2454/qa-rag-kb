# Iter 022 Evaluation

artifact:
  id: iter-022-eval
  type: evaluation
  stage: reviewing
  status: approved

evaluation:
  passed: true
  score: 90
  errors: []
  suggestions:
    - 下一轮应先按标题/描述形态拆分中等批次剩余 warning，再补更窄的 title-driven `expected` 恢复规则。
    - 对 `DEF-824272` 这类问句型或非 defect 条目，应先决定是阻断拒收还是转成单独分类。

## 1. 中等批次 importer 验收是否稳定

- 结果：FAIL
- 依据：
  - `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-022-check --defect-limit 20 --testcase-limit 20`
  - 结果：
    - `gate=warning`
    - `warnings=18`
    - `semantic_warnings=18`
    - `admissible_warnings=17`
    - `blocking_warnings=1`
    - `conflicts=0`
  - 对应 report：
    - `warning_code_distribution.missing_expected = 17`
    - `warning_code_distribution.missing_actual = 1`
    - `warning_code_distribution.testcase_steps_too_short = 1`
    - `quality_status = warning`

## 2. 剩余 warning 是否已被有效定位

- 结果：PASS
- 依据：
  - 17 条 `missing_expected` 主要来自 `expected_resolution = expected_missing_but_description_present`
  - 剩余样本可分成几类：
    - 标题直带期望语义但当前未恢复，例如 `没保存上`、`未显示全`、`没有回显`、`报 500/404`、`过账后才允许`
    - `问题若干 / 问题集合 / 需要产品确认 / 布局调整` 这类 bundle 或需求式条目
    - `DEF-824272` 这类既缺 `expected` 又缺 `actual` 的问句型记录
  - 说明：本轮已把问题从“warning 还很多”收敛为“剩余记录形态未覆盖”。

## 3. importer 与 loop 回归是否仍通过

- 结果：PASS
- 依据：
  - `python3 -m unittest tests/test_fixed_template_importer.py tests/test_validation_and_quality.py -v`
  - 结果：`Ran 35 tests ... OK`
  - `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`
  - 结果：`Ran 22 tests ... OK`
  - `python3 orchestrator/run.py loop --root .`
  - 结果：`loop iteration=22 ok=true stop_reason=none`

## 4. Phase 1 与 ruff loop 当前判断

- Phase 1：
  - 结果：PASS
  - 说明：按原始 `done_criteria` 仍然是已完成状态；本轮暴露的是“新恢复规则在更大样本上的稳定性不足”，不是 Phase 1 基础能力缺失。
- “完美完成”：
  - 结果：FAIL
  - 说明：中等批次仍为 `gate=warning`，因此当前 importer 基线还不能视为零剩余风险的完美签收。
- ruff loop：
  - 结果：PASS
  - 说明：作为当前仓库的一版最小 runner，loop 仍然闭环可用；问题已经不在 gate 传播或编排层，而回到 importer 质量层。

## 5. 总结

本轮验证目标已完成，并确认 Iter-021 的 `passed` 基线还不能直接外推到 `20 + 20` 中等批次。当前最合理的下一步不是继续动 loop，而是扩展更窄的 title-driven `expected` 恢复规则，并决定 bundle/问句型记录的准入策略。
