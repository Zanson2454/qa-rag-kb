# Iter-013 Autonomous Loop Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 `orchestrator v0` 基础上实现第一版本地自治 loop runner，能够围绕 Python / importer 迭代完成上下文装载、plan 校验、`ruff`、单测、batch run、状态更新和结果汇总，但不自动 `commit/push`。

**Architecture:** 保持 `orchestrator/run.py` 的 `next` 能力不变，新增一个面向本地执行的 `run_loop.py` 作为第一版 runner。runner 负责串联 `Context Loader -> Plan Gate -> Fast Gates -> Business Gates -> State Update`，把 `AGENTS.md`、`task-state.json`、`harness` 产物和 importer 命令组织成一条最小闭环；测试以 `tests/test_orchestrator_v0.py` 为基础新增独立的 loop runner 测试，避免把现有状态机测试搅混。

**Tech Stack:** Python 3.11、标准库 `subprocess/json/pathlib/dataclasses/unittest`、现有 `orchestrator` / `src/qa_kb_importer` / `tests`、外部命令 `ruff` / `python3 -m unittest`

---

### Task 1: 先写 loop runner 的失败测试

**Files:**
- Create: `tests/test_orchestrator_loop_runner.py`

- [ ] **Step 1: 写上下文装载测试**
  - 断言 runner 会检查：
    - 最近 `change record`
    - 最近 `review context`
    - `task-state.json`
    - 当前 iteration plan 文件
- [ ] **Step 2: 写 plan gate 阻断测试**
  - 断言 plan 缺失或 iteration 不匹配时，runner 返回失败且不进入门禁执行。
- [ ] **Step 3: 写 fast gates 成功路径测试**
  - 断言 `ruff` 和单测命令全部通过时，runner 会继续进入 business gate。
- [ ] **Step 4: 写 fast gates 失败停机测试**
  - 断言 `ruff` 或单测失败时，runner 会记录失败结果并停止，不继续跑 batch run。
- [ ] **Step 5: 写 business gate 成功路径测试**
  - 断言 batch run 成功后，runner 会汇总结果并更新状态摘要。
- [ ] **Step 6: 写 business gate 失败路径测试**
  - 断言 batch run 或质量门失败时，runner 会返回失败摘要，并标记需要 repair / human gate。
- [ ] **Step 7: 运行 `python3 -m unittest tests/test_orchestrator_loop_runner.py -v`，确认先失败**

### Task 2: 实现第一版 loop runner 与结果模型

**Files:**
- Create: `orchestrator/run_loop.py`

- [ ] **Step 1: 定义 runner 输入输出模型**
  - 至少包含：
    - 当前 iteration
    - plan 路径
    - fast gate 结果
    - business gate 结果
    - stop reason
- [ ] **Step 2: 实现 Context Loader**
  - 读取：
    - `AGENTS.md`
    - 最近 `change record`
    - 最近 `review context`
    - `task-state.json`
- [ ] **Step 3: 实现 Plan Gate**
  - 校验：
    - 当前 iteration 对应 plan 是否存在
    - plan 文件名是否与当前 iteration 对齐
    - 状态文件是否存在明显主线冲突
- [ ] **Step 4: 实现 Fast Gates**
  - 串行执行：
    - `ruff format --check`
    - `ruff check`
    - 相关 `python3 -m unittest ...`
- [ ] **Step 5: 实现 Business Gates**
  - 执行：
    - `PYTHONPATH=src python3 -m qa_kb_importer ...`
  - 解析返回值和标准输出摘要
- [ ] **Step 6: 返回结构化 runner 结果**
  - 供后续状态更新和 CLI 展示复用

### Task 3: 接入状态更新和命令入口

**Files:**
- Modify: `orchestrator/run.py`
- Modify: `orchestrator/README.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 为 `orchestrator/run.py` 增加新命令入口**
  - 例如：
    - `loop`
- [ ] **Step 2: 将 runner 结果回写到状态文件**
  - 至少补：
    - 最近 loop 结果
    - 是否触发 human gate
    - stop reason
- [ ] **Step 3: 确保不影响既有 `next` 命令**
- [ ] **Step 4: 更新 `orchestrator/README.md`**
  - 说明第一版 loop 的目标、范围、命令和限制
- [ ] **Step 5: 校对当前 `task-state.json` 字段是否足够承载 loop 摘要**
  - 若不足，再补最小字段，不额外扩复杂状态机

### Task 4: 补回归测试并验证既有 orchestrator 不回退

**Files:**
- Modify: `tests/test_orchestrator_v0.py`
- Modify: `tests/test_orchestrator_loop_runner.py`

- [ ] **Step 1: 补 `run.py loop` 命令入口测试**
- [ ] **Step 2: 补状态文件摘要写回测试**
- [ ] **Step 3: 回归既有 `next` 命令测试**
- [ ] **Step 4: 运行 `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`**
- [ ] **Step 5: 如仓库已补 `ruff` 配置，再运行 `ruff format --check` 与 `ruff check` 验证 runner 本身**

### Task 5: 用真实 importer 命令完成第一版闭环验收

**Files:**
- Modify: `docs/governance/autonomous-loop-design.md`
- Create: `harness/changes/iter-013-change.md`
- Create: `harness/evaluations/iter-013-eval.md`
- Create: `harness/reflections/iter-013-reflection.md`
- Create: `harness/review-contexts/iter-014-context.md`

- [ ] **Step 1: 用真实命令跑一次 loop**
  - 命令建议：
    - `python3 orchestrator/run.py loop --root .`
- [ ] **Step 2: 记录 fast gates 与 business gate 的真实结果**
- [ ] **Step 3: 编写本轮 evaluation**
  - 重点验证：
    - loop 是否能正确阻断 plan 缺失或状态冲突
    - loop 是否能串行执行 fast gates 和 business gates
    - loop 是否保持“本地闭环、不自动 push”
- [ ] **Step 4: 编写 reflection / change record / 下一轮 review context**
- [ ] **Step 5: 复核本轮没有遗留临时测试文件或一次性脚本**
