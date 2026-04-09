# Iter-023 One-Round Warning Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用最后 1 轮可控实现同时收敛中等批次 importer 的剩余高频 warning，并在本轮结束后强制停止 Phase 1 warning 优化。

**Architecture:** 本轮只允许改两类内容：`importer.py` 中最窄的 title-driven `expected` 恢复，以及 `validation.py` 中对 bundle/问句型非 defect 条目的准入分类。`quality.py`、`cli.py`、`run_loop.py` 不扩 scope；本轮结束后无论中等批次结果是 `passed` 还是“warning 但已完全分类”，都直接签收，不再继续 Phase 1 warning 调优。

**Tech Stack:** Python 3.11、标准库 `re/pathlib/unittest/tempfile`、PyYAML、现有 `src/qa_kb_importer`、`tests`、`harness`

---

### Task 1: 先把最后一轮允许解决的 warning 形态固定成失败测试

**Files:**
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 为 title-driven `expected` 恢复写失败测试**
  - 只覆盖当前中等批次已确认的 5 类标题语义：
    - `没保存上`
    - `未显示全`
    - `没有回显`
    - `报 500/404`
    - `过账后才允许`
  - 断言 importer 生成非空 `expected`，并继续保留 `expected_resolution` / `expected_source_section` / `generated_expected_candidate`。
- [ ] **Step 2: 为问句型非 defect 条目写失败测试**
  - 以 `DEF-824272` 类似样本为基线。
  - 断言这类既缺 `expected` 又缺 `actual`、标题/正文表现为问题确认或问句的记录，会产出显式分类 warning code，而不是继续混在普通 `missing_expected` 里。
- [ ] **Step 3: 为 bundle / 需求式条目写失败测试**
  - 以 `问题若干 / 问题集合 / 布局调整 / 需要产品确认` 为基线。
  - 断言这类记录不会强行自动补 `expected`，而会进入明确的 admissible 分类。
- [ ] **Step 4: 写中等批次验收回归断言**
  - 目标不是承诺 `warnings=0`，而是承诺：
    - `missing_expected` 明显下降
    - 问句型与 bundle 型记录不再混在普通 `missing_expected`
- [ ] **Step 5: 运行聚焦测试，确认先失败**
  - Run: `python3 -m unittest tests/test_fixed_template_importer.py tests/test_validation_and_quality.py -v`
  - Expected: 新增测试失败，说明当前规则尚未覆盖这些形态。

### Task 2: 在 importer 中实现最窄的 title-driven expected 恢复

**Files:**
- Modify: `src/qa_kb_importer/importer.py`

- [ ] **Step 1: 在现有 `_recover_defect_expected_candidate()` 之上增加标题驱动分支**
  - 先保留现有 description/title 症状恢复结构，不重构主流程。
- [ ] **Step 2: 只实现当前已明确的 5 类标题模式**
  - `没保存上` -> 保存后应生效/应保存成功
  - `未显示全` -> 信息应完整显示
  - `没有回显` -> 请求参数或界面值应正确回显
  - `报 500/404` -> 接口请求不应返回 500/404
  - `过账后才允许` -> 仅在过账后才允许执行相应动作
- [ ] **Step 3: 保持保守边界**
  - 不扩展到更多自由标题模式
  - 不为 `问题若干 / 问题集合 / 需求确认 / 布局调整` 生成 `expected`
- [ ] **Step 4: 继续保留恢复痕迹**
  - `expected_resolution = expected_generated_from_symptom`
  - `expected_source_section = 缺陷标题` 或更精确的标题来源
  - `quality_flags` 继续保留 `generated_expected_candidate`
- [ ] **Step 5: 运行 Task 1 的恢复测试，确认通过**

### Task 3: 在 validation 中拆出非 defect / bundle 型准入分类

**Files:**
- Modify: `src/qa_kb_importer/validation.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 为问句型非 defect 记录增加专用 warning code**
  - 例如 `question_like_record` 或等价命名。
  - admission 设为 `blocking`。
- [ ] **Step 2: 为 bundle / 需求式记录增加专用 warning code**
  - 例如 `bundle_like_record` 或等价命名。
  - admission 设为 `admissible`。
- [ ] **Step 3: 让这两类 code 从普通 `missing_expected` 中分离**
  - 目标是让 report 直接反映“剩余问题是什么”，而不是继续堆在一个大类里。
- [ ] **Step 4: 运行 validation / quality 测试**
  - Run: `python3 -m unittest tests/test_validation_and_quality.py -v`
  - Expected: 通过，并能看到新增分类被覆盖。

### Task 4: 只做一次中等批次重验，然后强制收口

**Files:**
- Review: `/tmp/qa-kb-iter-023-check/imports/reports/`

- [ ] **Step 1: 运行唯一一次真实 importer 中等批次重验**
  - Run: `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-023-check --defect-limit 20 --testcase-limit 20`
- [ ] **Step 2: 读取 report / details 并对照本轮目标**
  - 核对：
    - `gate`
    - `warning_count`
    - `warning_code_distribution`
    - `admissible_warning_count`
    - `blocking_warning_count`
    - `conflicts`
- [ ] **Step 3: 固定本轮 stop rule**
  - 无论结果如何，本轮结束后都不再继续 Phase 1 warning 调优。
  - 只允许两种结论之一：
    - `Sign off with improved baseline`
    - `Sign off with known limitations`
- [ ] **Step 4: 补跑 loop 验证**
  - Run: `python3 orchestrator/run.py loop --root .`
  - 目的：确认 loop 仍能消费更新后的 importer 基线。

### Task 5: 用文档正式签收，不再继续打磨

**Files:**
- Create: `harness/changes/iter-023-change.md`
- Create: `harness/evaluations/iter-023-eval.md`
- Create: `harness/reflections/iter-023-reflection.md`
- Create: `harness/review-contexts/iter-024-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 在 change record 中明确写入“本轮是最后 1 轮 warning closure”**
- [ ] **Step 2: 在 evaluation 中只允许写两种签收结论**
  - `improved baseline`
  - `known limitations`
- [ ] **Step 3: 在 reflection 中解释为什么本轮后停止继续优化**
- [ ] **Step 4: 更新 `task-state.json`**
  - 下一步切到“进入下一阶段”或“记录已知限制”，而不是继续 warning 调优
- [ ] **Step 5: 若验证完成，提交并推送本轮文件**
