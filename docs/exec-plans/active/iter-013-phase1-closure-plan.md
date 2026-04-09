# Iter-013 Phase 1 Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 收口 QA KB Phase 1 计划尚未闭环的最后能力，包括重复源 ID 检查、目标路径冲突处理、错误清单细化，以及进入检索层前的 warning 准入标准定稿。

**Architecture:** 保持现有固定模板 importer 结构不变，在 `importer.py` 中补批次级去重与目标冲突检查，并把错误清单从“空结构”升级为“包含 error_type/source/raw_excerpt 的正式产物”。`quality.py` 继续负责批次总结，但不新增新一轮质量策略。文档侧用 `import-runbook.md` 与本轮 harness 文档把 warning admission policy 固化为 Phase 1 准入标准。

**Tech Stack:** Python 3.11、标准库 `pathlib/unittest/collections`、PyYAML、现有 `src/qa_kb_importer` / `tests` / `docs/knowledge` / `harness`

---

### Task 1: 先写 Phase 1 closure 的失败测试

**Files:**
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 写同批次重复 source_id 的失败测试**
  - 断言重复记录不入库，且 error list 包含：
    - `error_type=duplicate_source_id`
    - `source_file`
    - `source_sheet`
    - `source_row`
    - `source_id`
    - `raw_excerpt`
- [ ] **Step 2: 写目标路径冲突测试**
  - 断言目标目录中已存在同名 normalized 文件时：
    - 当前批次不覆盖
    - error list 记录 `target_conflict`
- [ ] **Step 3: 写 manifest 冲突计数测试**
  - 断言 manifest 至少补：
    - `success_count`
    - `failure_count`
    - `conflict_count`
- [ ] **Step 4: 写 runbook 准入标准对应测试**
  - 断言 report 或返回结果包含当前 Phase 1 准入判断所需字段，不依赖口头解释。
- [ ] **Step 5: 运行 `python3 -m unittest tests/test_fixed_template_importer.py -v`，确认新测试先失败**

### Task 2: 在 importer 中补重复与冲突处理

**Files:**
- Modify: `src/qa_kb_importer/importer.py`

- [ ] **Step 1: 增加同批次 `source_id` 去重**
  - defect 与 testcase 分别检查，同一批次重复 source_id 直接记 error。
- [ ] **Step 2: 增加目标路径冲突检测**
  - 若目标 normalized 文件已存在，则不覆盖，写入 error list。
- [ ] **Step 3: 细化错误清单结构**
  - 至少输出：
    - `source_file`
    - `source_sheet`
    - `source_row`
    - `source_id`
    - `error_type`
    - `error_message`
    - `raw_excerpt`
- [ ] **Step 4: 让 manifest 显式区分 success / failure / conflict**
  - 与已有 `error_count` 保持兼容。
- [ ] **Step 5: 保持 `version=1` 的 Phase 1 边界**
  - 明确“当前只做冲突拦截，不做自动升版”。

### Task 3: 固化 Phase 1 准入标准

**Files:**
- Modify: `docs/knowledge/import-runbook.md`
- Modify: `src/qa_kb_importer/cli.py`

- [ ] **Step 1: 在 runbook 中明确 Phase 1 准入标准**
  - 至少说明：
    - `blocking warning` 阻断
    - `admissible warning` 可收录但不代表可直接进入检索层
    - 当前仍不做自动版本合并
- [ ] **Step 2: 在 CLI 输出中保留 conflict 摘要**
  - 至少补：
    - `conflicts=<count>`
- [ ] **Step 3: 明确进入下一阶段前的判断口径**
  - 让 report / runbook / CLI 三者口径一致。

### Task 4: 完成真实批次验证与文档闭环

**Files:**
- Create: `harness/changes/iter-013-change.md`
- Create: `harness/evaluations/iter-013-eval.md`
- Create: `harness/reflections/iter-013-reflection.md`
- Create: `harness/review-contexts/iter-014-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 运行 `python3 -m unittest tests/test_fixed_template_importer.py tests/test_validation_and_quality.py -v`**
- [ ] **Step 2: 运行 `python3 -m unittest tests/test_orchestrator_v0.py -v`**
- [ ] **Step 3: 运行一次真实中等批次导入并确认冲突策略不破坏当前结果**
  - `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-013-check --defect-limit 20 --testcase-limit 20`
- [ ] **Step 4: 编写本轮 change / evaluation / reflection**
  - 明确 Phase 1 是否已满足 done criteria
- [ ] **Step 5: 更新状态文件和下一轮 review context**
  - 若 Phase 1 已完成，则下一轮切到 Phase 2 前置判断
  - 若仍未完成，则明确剩余阻断项

### Task 5: 本轮结束前执行仓库约定

**Files:**
- Modify: `harness/evaluations/iter-013-eval.md`
- Modify: `harness/reflections/iter-013-reflection.md`
- Modify: `harness/changes/iter-013-change.md`
- Modify: `harness/review-contexts/iter-014-context.md`

- [ ] **Step 1: 复核本轮没有留下临时调试测试或一次性脚本**
- [ ] **Step 2: 只保留正式回归测试作为基线**
- [ ] **Step 3: 若评测通过，则提交并推送本轮代码与文档**
