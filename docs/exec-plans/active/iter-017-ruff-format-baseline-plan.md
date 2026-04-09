# Iter-017 Ruff Format Baseline Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 收敛仓库当前 `ruff format` 基线，使自治 loop 可以越过第一层 fast gate，并暴露下一个真实阻断点。

**Architecture:** 本轮不改 loop 架构，也不参数化 gates，只做格式基线收敛。先用 `ruff format --check .` 作为红灯验证，再用 `ruff format .` 统一格式，随后回归现有 orchestrator 测试和真实 `loop` 命令，确认新的第一阻断已经从格式问题推进到下一层。

**Tech Stack:** Ruff、Python 3.11、现有 `orchestrator` / `src/qa_kb_importer` / `tests` / `harness`

---

### Task 1: 先确认格式红灯范围

**Files:**
- Modify: `orchestrator/*.py`
- Modify: `src/qa_kb_importer/*.py`
- Modify: `tests/*.py`

- [ ] **Step 1: 运行 `ruff format --check .`**
- [ ] **Step 2: 记录需要收敛的文件范围**
- [ ] **Step 3: 确认本轮不引入临时脚本或一次性测试文件**

### Task 2: 收敛 ruff format 基线

**Files:**
- Modify: `orchestrator/artifacts.py`
- Modify: `orchestrator/prompting.py`
- Modify: `orchestrator/run.py`
- Modify: `orchestrator/run_loop.py`
- Modify: `orchestrator/state_machine.py`
- Modify: `orchestrator/validation.py`
- Modify: `src/qa_kb_importer/cli.py`
- Modify: `src/qa_kb_importer/importer.py`
- Modify: `src/qa_kb_importer/quality.py`
- Modify: `src/qa_kb_importer/validation.py`
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_orchestrator_loop_runner.py`
- Modify: `tests/test_orchestrator_v0.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 执行 `ruff format .`**
- [ ] **Step 2: 复核仅发生格式变更，没有混入行为修改**
- [ ] **Step 3: 如发现格式化引出语法或导入问题，做最小修正**

### Task 3: 验证 fast gate 已越过格式层

**Files:**
- Modify: `orchestrator/state/task-state.json`
- Create: `harness/changes/iter-017-change.md`
- Create: `harness/evaluations/iter-017-eval.md`
- Create: `harness/reflections/iter-017-reflection.md`
- Create: `harness/review-contexts/iter-018-context.md`

- [ ] **Step 1: 运行 `ruff format --check .`，确认变绿**
- [ ] **Step 2: 运行 `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`**
- [ ] **Step 3: 运行 `python3 orchestrator/run.py loop --root .`**
- [ ] **Step 4: 记录 loop 的新 stop reason**
- [ ] **Step 5: 编写 evaluation / reflection / change record / review context**
