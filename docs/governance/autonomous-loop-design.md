# Autonomous Iteration Loop Design

artifact:
  id: autonomous-loop-design
  type: design
  stage: designing
  status: approved

## 1. Goal

为当前仓库设计一条面向 Python / importer 迭代的本地自治 loop，使代理能够在不自动 `commit/push` 的前提下，围绕既有工程流程完成：

- 读取上下文
- 校验 plan
- 实现代码
- 运行 `ruff`
- 运行单测
- 运行业务批次验证
- 生成 evaluation / reflection / change record / review context
- 更新状态文件

目标不是替代现有 `AGENTS.md` 和 `orchestrator` 资产，而是把它们组织成一条可连续执行、可自主修复、带明确停机条件的迭代主线。

## 2. Scope

### In Scope

- 当前仓库的 Python / importer 代码迭代
- 本地执行的快速质量门和业务质量门
- 基于已有 `task-state.json` 的轮次推进
- 基于已有 `harness` 产物的评测闭环
- 自主 repair loop 与重试上限

### Out Of Scope

- 自动 `git commit`
- 自动 `git push`
- 文档治理轮次的全覆盖自治
- skill 治理轮次的全覆盖自治
- 多任务并行编排
- 远程 CI/CD 集成

## 3. Existing Assets To Reuse

自治 loop 必须直接复用以下现有资产，而不是另起一套：

- `AGENTS.md`
- `orchestrator/state/task-state.json`
- `orchestrator/state_machine.py`
- `orchestrator/run.py`
- `orchestrator/prompts/`
- `harness/changes/`
- `harness/evaluations/`
- `harness/reflections/`
- `harness/review-contexts/`
- `tests/`
- `src/qa_kb_importer/`

## 4. Design Principles

### 4.1 主状态机不由 Ruff 承担

`ruff` 只负责快速静态质量门，不负责轮次推进、业务判断或状态机调度。

### 4.2 先复用，再扩展

第一版只在现有 `orchestrator` 之上补最小 loop 能力，不新增重量级调度系统。

### 4.3 分层门禁

必须把“代码是否健康”和“业务是否可收口”拆成两层：

- 快速门禁：`ruff`、单测
- 业务门禁：batch run、quality gate、admission policy

### 4.4 明确停机

loop 可以自主修复，但不能无限循环。遇到状态冲突、策略分叉、重试超限时必须停机。

## 5. Loop Topology

第一版自治 loop 采用以下节点顺序：

```text
Context Loader
  -> Plan Gate
  -> Implement Step
  -> Fast Gates
  -> Business Gates
  -> Review Loop
  -> State Update
  -> Human Gate
```

### 5.1 Context Loader

职责：

- 读取 `AGENTS.md`
- 读取最近一轮 `change record`
- 读取最近 `review context`
- 读取 `task-state.json`
- 识别当前 iteration、目标、重试计数和下一步动作

阻断条件：

- 最近一轮 `change record` 缺失
- `review context` 缺失
- `task-state.json` 与实际计划文件不一致
- 同一 iteration 存在多个冲突主线

若命中阻断条件，loop 直接停机，不进入实现。

### 5.2 Plan Gate

职责：

- 确认存在本轮正式 `exec plan`
- 确认 plan 与当前 iteration 对齐
- 确认 plan 范围与 `review context` 一致

规则：

- 无 plan 不得进入实现
- plan 未对齐当前 iteration，不得进入实现

### 5.3 Implement Step

职责：

- 按 plan 执行最小代码改动
- 每次改动后进入门禁检查
- 允许小步修复，不允许跨越计划边界

约束：

- 临时测试文件和一次性脚本必须在本轮结束前收敛
- 若发现工作树存在冲突或明显状态分叉，停止当前 loop

### 5.4 Fast Gates

职责：

- 运行 `ruff format`
- 运行 `ruff check`
- 运行相关单测

结果分流：

- 全部通过：进入 `Business Gates`
- 可自动修复失败：回到 `Implement Step`
- 连续失败超限：进入停机

### 5.5 Business Gates

职责：

- 运行 importer 的 batch run
- 检查业务质量门，例如：
  - `gate`
  - `warning_rate`
  - `semantic_warning_rate`
  - `blocking/admissible` 分布

规则：

- 代码门通过但业务门失败，不允许结束本轮
- 若业务失败原因清晰且属于当前 plan 范围，允许进入 repair loop
- 若业务失败原因超出本轮 plan 范围，停机等待新 plan

### 5.6 Review Loop

职责：

- 生成或更新：
  - `evaluation`
  - `reflection`
  - `change record`
  - 下一轮 `review context`

要求：

- 评测必须基于实际执行结果
- 反思必须解释失败或通过的原因
- change record 必须记录风险和未解决问题

### 5.7 State Update

职责：

- 更新 `orchestrator/state/task-state.json`
- 写入当前 iteration 的完成状态、最近产物、下一步建议、重试计数

要求：

- 状态文件只能反映唯一主线
- 不允许把治理性文档轮次和代码实现轮次混成同一 iteration

### 5.8 Human Gate

职责：

- 结束本地 loop
- 保留人工决定是否 `commit/push`

第一版默认不自动进入 git 提交流程。

## 6. Retry And Stop Policy

### 6.1 Retry Classes

第一版定义两类重试：

- 快速修复重试：针对 `ruff` 或单测失败
- 业务修复重试：针对 batch run / quality gate 失败

### 6.2 Retry Caps

建议默认上限：

- 快速修复重试：最多 3 次
- 业务修复重试：最多 2 次

### 6.3 Stop Conditions

出现以下任一条件时，loop 必须停机：

- iteration 主线冲突
- 当前目标与 plan 不一致
- `task-state.json` 与 harness 证据链冲突
- 连续修复超过上限
- 发现需要人工决策的策略分叉
- 检测到高风险工作树冲突

## 7. Ruff Placement

`ruff` 在第一版 loop 中处于 `Fast Gates` 层，而不是总编排器。

职责包括：

- 自动格式化
- 快速发现 lint 问题
- 尽早阻断低级错误进入业务门

不承担：

- 轮次推进
- plan 管理
- admission policy 判断
- harness 文档闭环

## 8. First Version Runtime Contract

第一版最小运行合同如下：

### Inputs

- 当前仓库工作树
- `AGENTS.md`
- 当前 iteration 的 `exec plan`
- 最近 `change record`
- 最近 `review context`
- `task-state.json`

### Outputs

- 代码改动
- `ruff` 与测试结果
- batch run 结果
- 本轮 `evaluation`
- 本轮 `reflection`
- 本轮 `change record`
- 下一轮 `review context`
- 更新后的 `task-state.json`

### Required Commands

第一版至少支持以下命令族：

- `ruff format`
- `ruff check`
- `python3 -m unittest ...`
- `PYTHONPATH=src python3 -m qa_kb_importer ...`

## 9. Acceptance Criteria

第一版自治 loop 的设计验收标准如下：

1. 能基于现有 `task-state.json` 和 harness 资产装载上下文。
2. 能拒绝无 plan 或 iteration 冲突的执行。
3. 能把 `ruff`、单测和 batch run 组织成串行门禁。
4. 能在失败时区分“可修复重试”和“必须停机”。
5. 能在本地闭环结束前补齐 `evaluation / reflection / change record / review context`。
6. 不自动执行 `commit/push`。

## 10. Recommended First Implementation Slice

建议第一版只做一个最小 runner，例如：

- `orchestrator/run_loop.py`

该 runner 先覆盖：

1. 读取上下文
2. 校验 plan
3. 执行 `ruff`
4. 执行相关测试
5. 执行一次 batch run
6. 汇总结果
7. 更新状态文件

以下能力放到后续版本：

- 多轮自动 repair
- 文档轮次自治
- skill 轮次自治
- 自动生成更完整的 harness 正文
- git 提交与推送

## 11. Recommendation

当前最合适的推进顺序是：

1. 先审阅本设计文档
2. 基于该设计生成实现 plan
3. 以最小 runner 落第一版
4. 在真实 importer 迭代中验证 loop 是否稳定

## 12. First Validation Note

第一版 runner 落地后的首次真实验证表明：

- loop 能正确装载当前仓库状态与上下文
- loop 能在进入 `ruff` / 测试 / batch run 之前先执行 plan gate
- 当同一 iteration 存在多个主线 plan 时，loop 会以 `plan_conflict` 停机，而不是误进入实现

这说明第一版最关键的“先阻断状态分叉，再执行门禁”原则已经可执行。
