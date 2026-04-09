# Iter-020 Gate Semantics Revalidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 先重新验收 Iter-019 的 business gate 语义传递链路，只有在验收失败时才重开实现。

**Architecture:** 保持现有 `cli.py -> run_loop.py` 的控制信号链路不变，把本轮重点放在正式验收。`cli.py` 负责把 `gate=failed` 转成非零退出码，`run_loop.py` 负责把 business gate 返回码映射成 `ok/stop_reason`，真实 `loop` 运行结果用于证明当前链路在 warning 基线下没有误判。若任一验收点失败，再以最小补丁修复 `cli.py`、`run_loop.py` 或对应测试。

**Tech Stack:** Python 3.11、标准库 `unittest/tempfile/json/pathlib`、现有 `src/qa_kb_importer`、`orchestrator`、`tests`、`harness`

---

### Task 1: 固化本轮验收标准

**Files:**
- Review: `harness/changes/iter-019-change.md`
- Review: `harness/review-contexts/iter-020-context.md`
- Review: `orchestrator/state/task-state.json`
- Create: `docs/exec-plans/active/iter-020-gate-semantics-revalidation-plan.md`

- [ ] **Step 1: 复核上一轮 change record 中的目标、风险和未解决问题**
- [ ] **Step 2: 复核 review context 与 `task-state.json` 是否都把下一步指向 warning 来源分析，而不是继续修改 gate 传播链路**
- [ ] **Step 3: 明确本轮通过标准**
  - CLI 在 `gate=failed` 时返回非零退出码
  - loop 在 business gate 非零时返回 `ok=false` 且 `stop_reason=business_gate_failed`
  - loop 使用独立 `knowledge_root`
  - 真实 `python3 orchestrator/run.py loop --root .` 不再因为 gate 传播错误而误判

### Task 2: 执行聚焦验收，不先改实现

**Files:**
- Test: `tests/test_fixed_template_importer.py`
- Test: `tests/test_orchestrator_loop_runner.py`
- Review: `src/qa_kb_importer/cli.py`
- Review: `orchestrator/run_loop.py`

- [ ] **Step 1: 运行 CLI 返回码相关正式测试**
  - Run: `python3 -m unittest tests/test_fixed_template_importer.py -v`
- [ ] **Step 2: 运行 loop gate 传播相关正式测试**
  - Run: `python3 -m unittest tests/test_orchestrator_loop_runner.py -v`
- [ ] **Step 3: 运行真实 loop 验收**
  - Run: `python3 orchestrator/run.py loop --root .`
- [ ] **Step 4: 如有必要，运行 `run_local_loop` 摘要检查**
  - Run: `python3 -c 'import json; from pathlib import Path; from orchestrator.run_loop import run_local_loop; print(json.dumps(run_local_loop(Path(".")), ensure_ascii=False, indent=2))'`
- [ ] **Step 5: 判定本轮分流**
  - 若上述检查全部通过，本轮不改实现代码
  - 若任一检查失败，进入 Task 3 的最小修复流程

### Task 3: 仅在验收失败时进行最小修复

**Files:**
- Modify: `src/qa_kb_importer/cli.py`
- Modify: `orchestrator/run_loop.py`
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_orchestrator_loop_runner.py`

- [ ] **Step 1: 先把失败场景固定为正式测试**
- [ ] **Step 2: 只修复 gate 语义传递链路本身**
  - 不扩展到 importer 质量规则
  - 不扩展到 loop 的其他治理节点
- [ ] **Step 3: 重新运行 Task 2 的全部验收命令**

### Task 4: 完成本轮闭环

**Files:**
- Create: `harness/changes/iter-020-change.md`
- Create: `harness/evaluations/iter-020-eval.md`
- Create: `harness/reflections/iter-020-reflection.md`
- Create: `harness/review-contexts/iter-021-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 在 change record 中明确记录本轮是否真的发生代码修复**
- [ ] **Step 2: 在 evaluation 中基于真实执行结果给出通过或失败**
- [ ] **Step 3: 在 reflection 中解释为什么当前 loop 已可继续推进，或为什么仍需回到 gate 传播链路**
- [ ] **Step 4: 更新 `task-state.json`，把当前轮次推进到 Iter-020 的正式结果**
- [ ] **Step 5: 若本轮存在代码或配置改动且验收通过，提交并推送本轮产物**
