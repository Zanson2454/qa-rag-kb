# Iter-018 E402 Fast Gate Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复当前 `ruff check .` 暴露出的 `E402 Module level import not at top of file`，让自治 loop 尝试越过全部 fast gates，并暴露下一层真实阻断点。

**Architecture:** 本轮只处理 `tests/test_fixed_template_importer.py` 与 `tests/test_validation_and_quality.py` 的导入顺序，不改 loop 架构和业务逻辑。先复核两个文件现有未提交改动的边界，再做最小导入调整，随后回归 `ruff check`、orchestrator/governance 测试和真实 `loop`。

**Tech Stack:** Ruff、Python 3.11、标准库 `pathlib/sys/tempfile/unittest`、现有 `tests` / `orchestrator/state` / `harness`

---

### Task 1: 复核 E402 触发位置与文件现状

**Files:**
- Modify: `docs/exec-plans/active/iter-018-e402-fast-gate-fix-plan.md`
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 运行 `ruff check tests/test_fixed_template_importer.py tests/test_validation_and_quality.py`**
- [ ] **Step 2: 阅读两份测试文件，确认当前未提交改动与导入位置的关系**
- [ ] **Step 3: 明确本轮只做导入顺序调整，不混入行为修改**

### Task 2: 最小修复 E402

**Files:**
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 调整文件顶部导入和 `sys.path` 处理顺序，消除 `E402`**
- [ ] **Step 2: 复核 diff，确认仅为导入顺序与必要空行变更**
- [ ] **Step 3: 如 `ruff check` 暴露新的同类问题，做同级最小修复**

### Task 3: 验证 fast gate 和 loop 进展

**Files:**
- Modify: `orchestrator/state/task-state.json`
- Create: `harness/changes/iter-018-change.md`
- Create: `harness/evaluations/iter-018-eval.md`
- Create: `harness/reflections/iter-018-reflection.md`
- Create: `harness/review-contexts/iter-019-context.md`

- [ ] **Step 1: 运行 `ruff check .`**
- [ ] **Step 2: 运行 `python3 -m unittest tests/test_governance_assets.py -v`**
- [ ] **Step 3: 运行 `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`**
- [ ] **Step 4: 运行 `python3 orchestrator/run.py loop --root .`**
- [ ] **Step 5: 记录 loop 的新 stop reason，并写 evaluation / reflection / change record / review context**
