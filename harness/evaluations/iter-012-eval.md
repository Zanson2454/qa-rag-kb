# Iter 012 Evaluation

artifact:
  id: iter-012-eval
  type: evaluation
  stage: reviewing
  status: approved
  target: src/qa_kb_importer/

evaluation:
  passed: true
  score: 96
  errors: []
  suggestions:
    - 下一轮可评估是否要从 `缺陷描述*` 中生成候选 `expected`，进一步降低 admissible warning 占比。
    - 可继续把 validation details 从 section 级推进到源文本片段级，提升人工修复效率。
    - 在进入检索层前，应先把 warning admission policy 和“允许收录”的规则写成显式准入标准。

## 1. defect expected 是否已完成最小分类

- 结果：PASS
- 依据：
  - `src/qa_kb_importer/importer.py` 已输出：
    - `expected_resolution`
    - `expected_source_section`
  - 本轮固定闭集已落地：
    - `expected_section_present`
    - `expected_missing_but_description_present`
    - `expected_missing_unrecoverable`

## 2. warning detail 是否已支持 admission policy

- 结果：PASS
- 依据：
  - `src/qa_kb_importer/validation.py` 的 warning detail 已补：
    - `source_field`
    - `source_section`
    - `admission`
  - `missing_expected` 已按 defect expected 分类接入 admission 规则：
    - `expected_missing_but_description_present` => `admissible`
    - `expected_missing_unrecoverable` => `blocking`

## 3. batch gate 是否已按 admission policy 判断

- 结果：PASS
- 依据：
  - `src/qa_kb_importer/quality.py` 已固定：
    - `schema_fail_count > 0` => `failed`
    - `error_count > 0` => `failed`
    - `blocking_warning_rate > 0.30` => `failed`
    - `admissible_warning_rate > 0.10` 且未命中 `failed` => `warning`
    - 其他 => `passed`
  - report 已输出：
    - `admissible_warning_count`
    - `blocking_warning_count`
    - `admissible_warning_rate`
    - `blocking_warning_rate`
    - `admission_distribution`

## 4. importer / CLI / runbook 是否已对齐 admission 口径

- 结果：PASS
- 依据：
  - `src/qa_kb_importer/importer.py` 返回：
    - `admissible_warning_count`
    - `blocking_warning_count`
  - `src/qa_kb_importer/cli.py` 已打印：
    - `admissible_warnings`
    - `blocking_warnings`
  - `docs/knowledge/import-runbook.md` 已更新 admission policy 和 gate 解读。

## 5. 中等批次试运行是否已收敛到更贴近真实样本质量的结果

- 结果：PASS
- 依据：
  - 执行：
    - `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-012-check --defect-limit 20 --testcase-limit 20`
  - 结果：
    - `batch=batch-20260409T045128Z defects=20 testcases=20 errors=0 gate=warning`
  - 报告显示：
    - `quality_warning_count: 21`
    - `admissible_warning_count: 20`
    - `blocking_warning_count: 1`
    - `admissible_warning_rate: 0.5`
    - `blocking_warning_rate: 0.025`
  - 结论：
    - 先前大量 `missing_expected` 不再一律阻断收录，gate 已从 `failed` 收敛为 `warning`

## 6. 本轮是否仍停留在 Phase 1 范围内

- 结果：PASS
- 依据：
  - 没有实现检索、embedding、向量库或问答链路。
  - 没有扩展 Orchestrator 业务流程，只更新状态文件。
  - 只增强 importer 的收录策略、质量报告和验收口径。

## 7. 验证证据

- `python3 -m unittest tests/test_validation_and_quality.py -v`
- 结果：
  - `Ran 15 tests ... OK`
- `python3 -m unittest tests/test_fixed_template_importer.py -v`
- 结果：
  - `Ran 11 tests ... OK`
- `python3 -m unittest tests/test_orchestrator_v0.py -v`
- 结果：
  - `Ran 11 tests ... OK`
- `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-012-check --defect-limit 20 --testcase-limit 20`
- 结果：
  - 成功输出 `gate=warning`
  - 成功生成：
    - `/tmp/qa-kb-iter-012-check/imports/reports/batch-20260409T045128Z-report.yaml`
    - `/tmp/qa-kb-iter-012-check/imports/reports/batch-20260409T045128Z-validation-details.yaml`

## 8. 总结

本轮已把 defect `missing_expected` 从“统一视为阻断语义缺陷”收敛为“基于 source section 分类的 admission policy”，并把 gate 从 `failed` 收敛为更贴近真实样本质量的 `warning`。规则、测试和文档均已同步，因此评测结论为 `passed: true`。
