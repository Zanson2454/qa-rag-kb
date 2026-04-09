# Iter-015 Agents And Skills Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增强 `AGENTS.md` 的主线治理规则，并创建两个项目内 `skill`：`iteration-start-review` 与 `acceptance-closure`，把高频、稳定、易遗漏的流程沉淀为可复用规范。

**Architecture:** 本轮只做治理资产与流程沉淀，不改 importer 业务逻辑。`AGENTS.md` 负责全局硬规则，两个 `skills/` 目录负责具体高频流程。通过最小试运行记录证明 skill 边界清晰，并避免与 `AGENTS.md`、runbook、plan 模板职责重叠。

**Tech Stack:** Markdown、仓库现有治理文档、`docs/governance/skill-management.md`、`harness/` 闭环文档

---

### Task 1: 先写治理资产的失败测试/检查清单

**Files:**
- Modify: `tests/test_orchestrator_v0.py`
- Create: `tests/test_governance_assets.py`

- [ ] **Step 1: 写 `AGENTS.md` 规则存在性测试**
  - 断言新增规则文本已出现：
    - 单一主线约束
    - `task-state.json` 唯一状态源
    - 阶段完成必须对照 `done_criteria`
    - governance/documentation 与 implementation 不得共用 iteration
- [ ] **Step 2: 写项目内 skill 目录结构测试**
  - 断言存在：
    - `skills/iteration-start-review/SKILL.md`
    - `skills/acceptance-closure/SKILL.md`
- [ ] **Step 3: 写 skill metadata 完整性测试**
  - 断言两个 `SKILL.md` 至少包含：
    - `name`
    - `description`
    - `goal`
    - `trigger_conditions`
    - `inputs`
    - `outputs`
    - `acceptance_criteria`
    - `out_of_scope`
    - `owner`
    - `dependencies`
- [ ] **Step 4: 运行相关测试并确认先失败**
  - `python3 -m unittest tests/test_governance_assets.py -v`

### Task 2: 增强 `AGENTS.md` 的主线治理规则

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: 增加单一主线约束**
  - 同一 iteration 不允许并行推进两个不同主题主线。
- [ ] **Step 2: 增加状态源优先级规则**
  - `task-state.json` 是当前确认主线的唯一状态源。
- [ ] **Step 3: 增加阶段完成判定规则**
  - 判断某阶段是否完成时，必须显式对照对应 plan 的 `done_criteria`。
- [ ] **Step 4: 增加治理线 / 实现线分离规则**
  - governance/documentation 主线与 implementation 主线不得共用 iteration 编号。

### Task 3: 创建第一个项目内 skill：`iteration-start-review`

**Files:**
- Create: `skills/iteration-start-review/SKILL.md`

- [ ] **Step 1: 定义 skill 目标与触发条件**
- [ ] **Step 2: 约束输入与输出**
  - 输入至少包括：
    - 最近一轮 change
    - review context
    - `task-state.json`
  - 输出至少包括：
    - review context summary
    - 主线冲突判断
    - 是否可进入本轮 plan
- [ ] **Step 3: 明确不与 `AGENTS.md` 重叠的边界**
- [ ] **Step 4: 写清 acceptance criteria**

### Task 4: 创建第二个项目内 skill：`acceptance-closure`

**Files:**
- Create: `skills/acceptance-closure/SKILL.md`

- [ ] **Step 1: 定义 skill 目标与触发条件**
- [ ] **Step 2: 约束输入与输出**
  - 输入至少包括：
    - 本轮 plan
    - 已改文件
    - 正式测试命令
    - 业务验证命令
  - 输出至少包括：
    - evaluation
    - reflection
    - change record
    - review context
    - 状态文件更新前检查
- [ ] **Step 3: 写清 commit / push 只在验收通过后触发**
- [ ] **Step 4: 明确不替代 runbook / 测试基线**

### Task 5: 固化最小试运行记录与本轮闭环

**Files:**
- Create: `docs/governance/skill-trials/iter-015-skills-trial.md`
- Create: `harness/changes/iter-015-change.md`
- Create: `harness/evaluations/iter-015-eval.md`
- Create: `harness/reflections/iter-015-reflection.md`
- Create: `harness/review-contexts/iter-016-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 记录两个 skill 的试运行边界**
  - 说明触发场景、收益、模糊点。
- [ ] **Step 2: 运行治理测试与现有 orchestrator 测试**
  - `python3 -m unittest tests/test_governance_assets.py -v`
  - `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`
- [ ] **Step 3: 编写本轮 evaluation / reflection / change record**
- [ ] **Step 4: 更新 `task-state.json` 与下一轮 review context**
- [ ] **Step 5: 若验收通过，则提交并推送本轮改动**
