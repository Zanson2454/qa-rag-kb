# Orchestrator v0

Orchestrator v0 的目标是把当前 QA Knowledge Base Harness 中“人工判断下一步、拼接 prompt、确认状态”的过程收敛成一个最小调度器。

## 当前支持范围

- 单任务调度
- 本地命令：
  - `next`
  - `loop`
- 基于 `orchestrator/state/task-state.json` 的状态推进
- 读取最近一轮 `change`、`evaluation`、`reflection`、`review-context`
- 生成给 Codex 的 prompt 文件到 `orchestrator/runs/`
- 支持的最小状态：
  - `created`
  - `planning`
  - `implementing`
  - `evaluating`
  - `reflecting`
  - `completed`
  - `blocked`
  - `failed`

## 如何执行 `next`

```bash
python3 orchestrator/run.py next
```

## 如何执行第一版本地自治 loop

```bash
python3 orchestrator/run.py loop
```

第一版 `loop` 的目标是串联最小本地闭环：

- 读取 `AGENTS.md`
- 读取最近一轮 `change record`
- 读取最近 `review context`
- 校验当前 iteration 对应的 exec plan
- 执行 `ruff format --check`
- 执行 `ruff check`
- 执行最小单测
- 执行一次 importer batch run
- 将本次 loop 摘要写回 `task-state.json`

当前 `loop` 只做本地执行，不自动 `commit/push`。

为了避免历史 iteration 下存在多个 plan 文件时产生歧义，状态文件可以显式提供：

- `current_plan.iteration`
- `current_plan.path`

当该字段存在时，`loop` 会优先使用它作为 canonical plan，而不是继续依赖“同轮只有一个 plan 文件”的假设。

## 状态文件

`orchestrator/state/task-state.json` 当前至少包含：

- `task_id`
- `current_iteration`
- `current_state`
- `current_goal`
- `last_outputs`
- `decision`
- `limits`

## 当前限制

- 尚未自动调用 Codex
- 尚未支持多任务并发
- 尚未提供 UI
- 当前规则是固定最小版，只覆盖 `passed/blocked/failed` 等基础分支
- 当前会严格校验 `task-state.json` 的必填字段和状态值
- 当前会校验 prompt 渲染后是否仍残留未替换占位符
- 当前 `loop` 只覆盖 Python / importer 主线，不覆盖文档治理或 skill 治理轮次
- 当前 `loop` 还没有完整 repair loop，只做最小 gate 串联和停机判断
- 当前 `loop` 的测试命令和 batch run 命令仍是固定最小版，后续需要继续参数化
