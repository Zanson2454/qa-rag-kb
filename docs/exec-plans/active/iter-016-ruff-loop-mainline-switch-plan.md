# Iter-016 Ruff Loop Mainline Switch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前仓库主线从 Iter-015 的治理/skill 主题正式切回 `ruff loop` 收敛主题，并把状态、评测与下一轮上下文对齐到可继续执行 `ruff format` 基线计划的状态。

**Architecture:** 本轮不执行 `ruff format` 基线收敛本身，只处理主线切换与状态对齐。通过 review 既有 `ruff loop` review context 和现有 `iter-015-ruff-format-baseline-plan.md`，新建一轮专门的切线计划，随后更新 `task-state.json` 与 harness 文档，明确下一轮应执行 `ruff format` 基线计划。

**Tech Stack:** Markdown、JSON、现有 `harness` / `docs/exec-plans` / `orchestrator/state`

---

### Task 1: 确认切线依据与目标主线

**Files:**
- Modify: `docs/exec-plans/active/iter-016-ruff-loop-mainline-switch-plan.md`

- [ ] **Step 1: review 最近一轮治理线 change 与 review context**
- [ ] **Step 2: review 既有 `ruff loop` review context 与 `iter-015-ruff-format-baseline-plan.md`**
- [ ] **Step 3: 明确本轮只做主线切回，不直接执行 `ruff format` 收敛**

### Task 2: 更新当前主线状态

**Files:**
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 将 `current_iteration` 切到 `16`**
- [ ] **Step 2: 将 `current_goal` 改为“切回 ruff loop 主线并准备执行 ruff format 基线计划”**
- [ ] **Step 3: 将 `current_plan` 指向本轮切线计划**
- [ ] **Step 4: 在 `decision.reason` 中明确下一轮执行 `docs/exec-plans/active/iter-015-ruff-format-baseline-plan.md`**
- [ ] **Step 5: 保留历史治理线记录，并补本轮主线切换记录**

### Task 3: 补齐本轮闭环文档

**Files:**
- Create: `harness/changes/iter-016-change.md`
- Create: `harness/evaluations/iter-016-eval.md`
- Create: `harness/reflections/iter-016-reflection.md`
- Create: `harness/review-contexts/iter-017-context.md`

- [ ] **Step 1: 在 change record 中记录切线原因、影响文件、风险和未解决问题**
- [ ] **Step 2: 在 evaluation 中说明本轮目标是“主线切换完成”，不是 `ruff format` 已收敛**
- [ ] **Step 3: 在 reflection 中记录为何将治理线与实现线拆成独立 iteration**
- [ ] **Step 4: 在下一轮 review context 中明确真正要执行的是 `iter-015-ruff-format-baseline-plan.md`**

### Task 4: 做最小一致性验证

**Files:**
- Modify: `tests/test_orchestrator_v0.py`
- Modify: `orchestrator/state/task-state.json`
- Modify: `harness/evaluations/iter-016-eval.md`

- [ ] **Step 1: 运行 `python3 -m unittest tests/test_orchestrator_v0.py -v`**
- [ ] **Step 2: 确认 repository state file 测试通过，且 `current_plan.iteration == current_iteration`**
- [ ] **Step 3: 将真实验证结果写回本轮 evaluation**
