# Iter-022 Medium Batch Stability Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `20 defect + 20 testcase` 的中等批次上重新验证 Iter-021 的 defect `expected` 候选恢复规则，确认 importer 质量基线是否稳定。

**Architecture:** 本轮不扩展新的 importer 规则，也不修改 loop 编排；只复用现有 `importer -> validation -> quality -> cli -> loop` 链路做更大样本验收。若中等批次继续保持 `gate=passed` 或维持可解释且稳定的轻量 warning，则固化为新的 importer 基线；若出现回归，则只记录 warning 分布、来源与影响，作为下一轮实现输入。

**Tech Stack:** Python 3.11、标准库 `pathlib/json/tempfile/unittest`、PyYAML、现有 `src/qa_kb_importer`、`orchestrator`、`tests`、`harness`

---

### Task 1: 固化本轮验收范围与成功标准

**Files:**
- Create: `docs/exec-plans/active/iter-022-medium-batch-stability-validation-plan.md`
- Review: `harness/changes/iter-021-change.md`
- Review: `harness/review-contexts/iter-022-context.md`
- Review: `orchestrator/state/task-state.json`

- [ ] **Step 1: 复核上一轮 change、review context 和状态文件**
  - 确认本轮目标只剩“中等批次稳定性验证”，不重开 gate 语义或 loop 基础设施。
- [ ] **Step 2: 固化样本规模与命令**
  - 使用：
    - `--defect-limit 20`
    - `--testcase-limit 20`
  - 命令固定为：
    - `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-022-check --defect-limit 20 --testcase-limit 20`
- [ ] **Step 3: 固化本轮通过标准**
  - 至少记录：
    - `gate`
    - `warning_count`
    - `warning_code_distribution`
    - `admissible_warning_count`
    - `blocking_warning_count`
    - `conflicts`
  - 判定规则：
    - `gate=passed` 且 `warnings=0` 视为直接通过
    - `gate=warning` 但 warning 分类稳定且可解释时，视为“部分通过，需要下一轮继续收敛”
    - `gate=failed` 或出现新的 blocking/conflict 回归，视为未通过

### Task 2: 运行中等批次 importer 验收并读取证据

**Files:**
- Review: `/tmp/qa-kb-iter-022-check/imports/reports/`

- [ ] **Step 1: 运行真实 importer 中等批次验收**
  - Run: `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-022-check --defect-limit 20 --testcase-limit 20`
- [ ] **Step 2: 读取最新 report 与 validation details**
  - 核对：
    - `input_record_count`
    - `quality_status`
    - `warning_count`
    - `warning_code_distribution`
    - `admissible_warning_count`
    - `blocking_warning_count`
    - `conflicts`
- [ ] **Step 3: 定位 warning 来源**
  - 若仍有 warning，按 `record_id`、`code`、`source_section` 统计主要来源。
  - 明确 warning 是否仍集中于 defect `expected` 候选恢复相关逻辑。

### Task 3: 运行回归测试，确认稳定性问题不来自其他回归

**Files:**
- Review: `tests/test_fixed_template_importer.py`
- Review: `tests/test_validation_and_quality.py`
- Review: `tests/test_orchestrator_v0.py`
- Review: `tests/test_orchestrator_loop_runner.py`

- [ ] **Step 1: 运行 importer 质量相关测试**
  - Run: `python3 -m unittest tests/test_fixed_template_importer.py tests/test_validation_and_quality.py -v`
- [ ] **Step 2: 运行 loop 相关回归测试**
  - Run: `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`
- [ ] **Step 3: 视需要运行真实 loop**
  - Run: `python3 orchestrator/run.py loop --root .`
  - 目的：确认 loop 仍能消费当前 importer 基线

### Task 4: 完成本轮 evaluation / reflection / change / review context

**Files:**
- Create: `harness/changes/iter-022-change.md`
- Create: `harness/evaluations/iter-022-eval.md`
- Create: `harness/reflections/iter-022-reflection.md`
- Create: `harness/review-contexts/iter-023-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 在 change record 里记录本轮实际运行命令、证据文件、风险和未解决问题**
- [ ] **Step 2: 在 evaluation 里写明中等批次是否稳定，以及 Phase 1 与 loop 的当前判断**
- [ ] **Step 3: 在 reflection 里说明当前 importer passed 基线是否可以外推到更大样本**
- [ ] **Step 4: 更新 `task-state.json`**
  - 若中等批次通过：把下一步切到“固化 importer passed 基线或进入下一阶段”
  - 若中等批次未通过：把下一步切到“收敛新的 warning 分类”
- [ ] **Step 5: 若本轮验证与文档完成，提交并推送本轮文件**
