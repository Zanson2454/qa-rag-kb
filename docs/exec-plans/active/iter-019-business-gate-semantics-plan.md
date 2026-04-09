# Iter-019 Business Gate Semantics Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 对齐自治 loop 与 importer CLI 的 business gate 失败语义，让 `gate=failed` 能通过退出码传播给 loop，并避免 loop 重跑时污染正式 `docs/knowledge` 目录。

**Architecture:** 采用“控制信号与证据信号分离”的最佳实践。`src/qa_kb_importer/cli.py` 负责根据 batch `gate` 返回稳定退出码；`orchestrator/run_loop.py` 继续只按返回码判定 business gate 成败，但改为给 importer 传递 loop 专用 `knowledge_root`，避免固定落在 `docs/knowledge` 上造成重复冲突。测试覆盖 CLI 退出码、loop business gate 失败传播、以及独立 knowledge root 参数。

**Tech Stack:** Python 3.11、标准库 `tempfile/pathlib/json/unittest`、现有 `src/qa_kb_importer` / `orchestrator` / `tests` / `harness`

---

### Task 1: 先写 business gate 语义测试

**Files:**
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_orchestrator_loop_runner.py`

- [ ] **Step 1: 为 CLI 增加 `gate=failed` 返回非零的测试**
- [ ] **Step 2: 为 CLI 保留 `gate=warning` 返回零的既有测试**
- [ ] **Step 3: 为 loop 增加 business command 包含独立 `--knowledge-root` 的测试**
- [ ] **Step 4: 为 loop 增加“business gate 返回非零即 stop_reason=business_gate_failed”的聚焦测试**

### Task 2: 实现 CLI 失败退出码与 loop 独立 knowledge root

**Files:**
- Modify: `src/qa_kb_importer/cli.py`
- Modify: `orchestrator/run_loop.py`

- [ ] **Step 1: 在 CLI 中根据 `result['gate']` 返回退出码**
- [ ] **Step 2: 在 loop 中为 business gate 构造独立的 `knowledge_root`**
- [ ] **Step 3: 确保 loop 重跑不会继续写入正式 `docs/knowledge`**
- [ ] **Step 4: 保持 loop 仍只按退出码判断成功/失败，不引入 stdout 解析**

### Task 3: 验证最佳实践链路

**Files:**
- Modify: `orchestrator/state/task-state.json`
- Create: `harness/changes/iter-019-change.md`
- Create: `harness/evaluations/iter-019-eval.md`
- Create: `harness/reflections/iter-019-reflection.md`
- Create: `harness/review-contexts/iter-020-context.md`

- [ ] **Step 1: 运行 `ruff format --check .`**
- [ ] **Step 2: 运行 `ruff check .`**
- [ ] **Step 3: 运行 `python3 -m unittest tests/test_fixed_template_importer.py tests/test_governance_assets.py tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`**
- [ ] **Step 4: 运行 `python3 orchestrator/run.py loop --root .`**
- [ ] **Step 5: 如有必要，运行 `python3 -c 'import json; from pathlib import Path; from orchestrator.run_loop import run_local_loop; print(json.dumps(run_local_loop(Path(".")), ensure_ascii=False, indent=2))'` 定位结果**
- [ ] **Step 6: 写 evaluation / reflection / change record / review context，并更新 `task-state.json`**
