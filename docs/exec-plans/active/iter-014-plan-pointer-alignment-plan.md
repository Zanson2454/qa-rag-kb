# Iter-014 Canonical Plan Pointer Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `task-state.json` 增加当前 iteration 的显式主线 plan 指针，消除历史多 plan 并存导致的 `plan_conflict`，让自治 loop 能基于唯一 plan 继续推进真实 importer 迭代。

**Architecture:** 保持现有 `docs/exec-plans/active/` 不做大规模迁移，在状态文件中新增最小字段记录“当前 iteration 的 canonical plan”。`run_loop.py` 优先读取该字段；若字段缺失，再退回旧的唯一 plan 搜索逻辑。`validation.py` 负责校验该字段与当前 iteration 一致，测试覆盖显式 plan、缺失 plan、错配 plan 和历史多 plan 并存场景。

**Tech Stack:** Python 3.11、标准库 `json/pathlib/unittest`、现有 `orchestrator` / `tests`

---

### Task 1: 先写 canonical plan pointer 的失败测试

**Files:**
- Modify: `tests/test_orchestrator_loop_runner.py`
- Modify: `tests/test_orchestrator_v0.py`

- [ ] **Step 1: 写显式 current plan 覆盖多 plan 冲突测试**
- [ ] **Step 2: 写 current plan 缺失文件时的阻断测试**
- [ ] **Step 3: 写 current plan iteration 不匹配时的阻断测试**
- [ ] **Step 4: 写 `run.py loop` 会保留 current plan 摘要的测试**
- [ ] **Step 5: 运行相关测试，确认先失败**

### Task 2: 在状态校验与 loop 中接入 canonical plan pointer

**Files:**
- Modify: `orchestrator/validation.py`
- Modify: `orchestrator/run_loop.py`

- [ ] **Step 1: 定义 `current_plan` 的最小字段结构**
  - 至少包含：
    - `iteration`
    - `path`
- [ ] **Step 2: 在状态校验中校验 `current_plan` 与 `current_iteration` 一致**
- [ ] **Step 3: 让 loop 优先读取 `current_plan.path`**
- [ ] **Step 4: 当 `current_plan` 明确存在时，不再把历史多 plan 直接判成冲突**
- [ ] **Step 5: 保留对缺失 / 错配 / 文件不存在的阻断逻辑**

### Task 3: 更新命令入口和仓库状态

**Files:**
- Modify: `orchestrator/run.py`
- Modify: `orchestrator/README.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 让 `loop` 结果摘要带上 canonical plan 路径**
- [ ] **Step 2: 更新 README，说明 `current_plan` 的作用**
- [ ] **Step 3: 在仓库状态文件中写入当前 iteration 的 canonical plan**

### Task 4: 验证并补闭环文档

**Files:**
- Create: `harness/changes/iter-014-change.md`
- Create: `harness/evaluations/iter-014-eval.md`
- Create: `harness/reflections/iter-014-reflection.md`
- Create: `harness/review-contexts/iter-015-context.md`

- [ ] **Step 1: 运行 `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`**
- [ ] **Step 2: 运行 `python3 orchestrator/run.py loop --root .`**
- [ ] **Step 3: 记录 canonical plan 已消除 `plan_conflict` 还是暴露了新的阻断**
- [ ] **Step 4: 编写 evaluation / reflection / change record / review context**
