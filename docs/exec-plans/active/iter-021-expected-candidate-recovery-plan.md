# Iter-021 Expected Candidate Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为缺失结构化 `expected` 的 defect 增加最小候选补全能力，把当前 `warnings=3` 收敛为可验证的更低基线。

**Architecture:** 保持现有 `importer -> validation -> quality` 链路不变，只在 `importer.py` 中为少量高置信模式生成 `expected` 候选，并保留显式来源与质量标记。`validation.py` 继续使用已有 `missing_expected` 规则；只要 importer 成功补出 `expected`，warning 会自然消失。`quality.py` 不改 gate 语义，只通过回归报告验证 warning 数量是否下降。

**Tech Stack:** Python 3.11、标准库 `re/pathlib/unittest/tempfile`、PyYAML、现有 `src/qa_kb_importer`、`tests`、`harness`

---

### Task 1: 先把 3 个 warning 的业务模式固定成失败测试

**Files:**
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 为 `失败` 症状写 defect expected 候选恢复测试**
  - 构造仅有 `缺陷描述*` 的 defect，正文包含“导入失败”或“任务执行失败”。
  - 断言 importer 会生成非空 `expected`。
  - 断言会写入新的 `expected_resolution` 与 `expected_source_section`。
- [ ] **Step 2: 为 `不一致` 症状写 defect expected 候选恢复测试**
  - 构造正文包含“数据不一致”。
  - 断言 importer 生成“应一致”语义的 `expected` 候选。
- [ ] **Step 3: 为 `报错...为空` 症状写 defect expected 候选恢复测试**
  - 构造正文包含“报错销售渠道为空”。
  - 断言 importer 生成“不应报错销售渠道为空”或等价候选。
- [ ] **Step 4: 写 validation 回归测试**
  - 断言已生成候选 `expected` 的 defect 不再触发 `missing_expected`。
  - 断言仍保留显式质量标记，避免把自动补全误当原始结构化字段。
- [ ] **Step 5: 运行聚焦测试，确认先失败**
  - Run: `python3 -m unittest tests/test_fixed_template_importer.py tests/test_validation_and_quality.py -v`
  - 预期：新增测试失败，说明当前代码还不会生成候选 `expected`。

### Task 2: 在 importer 中实现最小 expected 候选恢复

**Files:**
- Modify: `src/qa_kb_importer/importer.py`

- [ ] **Step 1: 为 defect expected 缺失新增专用恢复函数**
  - 只接受标题与 `缺陷描述*` 文本。
  - 输出：
    - `expected_candidate`
    - `expected_resolution`
    - `expected_source_section`
    - 是否应追加质量标记
- [ ] **Step 2: 只支持当前样本已验证的高置信模式**
  - `失败` -> 生成“操作应成功/不应失败”语义候选
  - `不一致` -> 生成“相关结果应一致”语义候选
  - `报错...为空` -> 生成“不应报错...为空”语义候选
- [ ] **Step 3: 保持保守策略**
  - 若未命中模式，仍保持 `expected` 为空
  - 仍保留 `expected_missing_unrecoverable` 或等价未恢复状态
- [ ] **Step 4: 为成功恢复的记录补显式元信息**
  - 例如：
    - `expected_resolution = expected_generated_from_symptom`
    - `expected_source_section = 缺陷标题` 或 `缺陷描述*`
    - `quality_flags` 新增 `generated_expected_candidate`
- [ ] **Step 5: 运行 Task 1 测试，确认恢复逻辑通过**

### Task 3: 验证 warning 是否从当前基线收敛

**Files:**
- Review: `src/qa_kb_importer/validation.py`
- Review: `src/qa_kb_importer/quality.py`
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 确认无需修改 gate 传播逻辑**
  - 不改 `cli.py`
  - 不改 `orchestrator/run_loop.py`
- [ ] **Step 2: 补回归测试**
  - 断言生成候选 `expected` 后，`warning_code_distribution` 不再包含当前 3 条 `missing_expected`
  - 断言 `admissible_warning_count` 与 `warning_rate` 下降
- [ ] **Step 3: 运行正式测试**
  - Run: `python3 -m unittest tests/test_fixed_template_importer.py tests/test_validation_and_quality.py -v`
  - 预期：全部通过
- [ ] **Step 4: 运行 loop 相关回归，确认未影响编排层**
  - Run: `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`
  - 预期：全部通过

### Task 4: 运行真实 importer 验收并判断 warning 是否可清零

**Files:**
- Review: `/tmp/qa-kb-iter-021-check/` 运行产物

- [ ] **Step 1: 运行真实 importer 验收**
  - Run: `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-021-check`
- [ ] **Step 2: 检查真实 batch report**
  - 核对：
    - `warning_count`
    - `warning_code_distribution`
    - `admissible_warning_count`
    - `gate`
- [ ] **Step 3: 判定本轮是否达成目标**
  - 若 `warnings=0` 或明显下降且原因可解释，视为通过
  - 若仍有 warning，必须在 evaluation 中明确是哪一类没有被本轮设计覆盖

### Task 5: 完成本轮闭环

**Files:**
- Create: `harness/changes/iter-021-change.md`
- Create: `harness/evaluations/iter-021-eval.md`
- Create: `harness/reflections/iter-021-reflection.md`
- Create: `harness/review-contexts/iter-022-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 在 change record 中记录本轮新增的候选补全规则、风险和未解决问题**
- [ ] **Step 2: 在 evaluation 中写明真实 warning 是否下降，以及当前 gate 是否变化**
- [ ] **Step 3: 在 reflection 中解释该启发式是否足够保守**
- [ ] **Step 4: 更新 `task-state.json`，把下一步切到“继续收敛 warning”或“固化新基线”**
- [ ] **Step 5: 若测试与验收通过，提交并推送本轮文件**
