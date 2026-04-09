---
name: acceptance-closure
description: Use near the end of an iteration in this repository to run formal verification, execute real acceptance checks, write evaluation/reflection/change/review-context artifacts, update task-state, and prepare commit/push.
---

## goal

在一轮实现接近结束时，固定执行正式测试、业务验收、文档闭环和状态同步，确保每轮都能以可验证证据收口，而不是停留在口头结论。

## trigger_conditions

- 本轮实现已基本完成
- 需要判断是否满足 Definition of Done
- 需要生成 `evaluation / reflection / change record / review context`

## inputs

- 当前 iteration 的 exec plan
- 本轮已改文件列表
- 正式测试命令
- 真实业务验证命令
- `orchestrator/state/task-state.json`

## outputs

- `evaluation`
- `reflection`
- `change record`
- 下一轮 `review context`
- 状态文件更新前检查结果
- commit / push 前的验收结论

## acceptance_criteria

- 已运行正式测试并记录结果
- 已运行至少一条真实业务验收命令并记录结果
- 已补齐 `evaluation / reflection / change record / review context`
- 已更新 `task-state.json` 到当前唯一主线
- 若验收通过，已准备进入 commit / push

## out_of_scope

- 不替代 runbook 中的具体命令说明
- 不替代测试文件本身
- 不负责定义本轮 plan
- 不负责在失败时自动改代码

## owner

- 当前仓库维护者与执行代理

## dependencies

- `AGENTS.md`
- 当前 iteration 的 exec plan
- `harness/evaluations/`
- `harness/reflections/`
- `harness/changes/`
- `harness/review-contexts/`
- `orchestrator/state/task-state.json`
