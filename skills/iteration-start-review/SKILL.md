---
name: iteration-start-review
description: Use when starting a new iteration in this repository to review the latest change record, read review context, validate task-state alignment, and detect mainline conflicts before writing the next plan.
---

## goal

在进入新一轮 plan 之前，固定完成最近一轮产物 review、状态文件对齐检查和主线冲突判断，降低 iteration 分叉和错误续写风险。

## trigger_conditions

- 开始新的 iteration
- 需要根据最近一轮结果决定下一步 plan
- 发现 `task-state.json`、change record、review context 之间可能不一致

## inputs

- 最近一轮 `harness/changes/<iter>-change.md`
- 最近一轮 `harness/review-contexts/<iter+1>-context.md`
- `orchestrator/state/task-state.json`
- 当前用户请求或当前阶段目标

## outputs

- 本轮 `review context` 摘要
- 主线是否一致的判断
- 是否允许进入本轮 plan 的结论
- 若有冲突，需要人工确认的阻断说明

## acceptance_criteria

- 已明确最近一轮 change record 的目标、风险、未解决问题
- 已明确 review context 中的下一轮优先事项
- 已检查 `task-state.json` 是否指向当前确认主线
- 若存在主线冲突，已停止继续实现并请求人工确认

## out_of_scope

- 不负责编写本轮 exec plan
- 不负责编写实现代码
- 不替代 `AGENTS.md` 的全局工作规则
- 不负责 commit / push

## owner

- 当前仓库维护者与执行代理

## dependencies

- `AGENTS.md`
- `orchestrator/state/task-state.json`
- `harness/changes/`
- `harness/review-contexts/`
- 当前阶段对应的 exec plan
