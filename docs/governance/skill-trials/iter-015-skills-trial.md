# Iter 015 Skills Trial Record

artifact:
  id: iter-015-skills-trial
  type: trial
  stage: reviewing
  status: approved

## Trial Scope

本轮试运行的项目内 skill：

- `iteration-start-review`
- `acceptance-closure`

## Trigger Scenarios

### `iteration-start-review`

- 用于每轮开始前：
  - review 最近一轮 change
  - 读取 review context
  - 校验 `task-state.json`
  - 判断是否存在主线冲突

### `acceptance-closure`

- 用于每轮结束前：
  - 跑正式测试
  - 跑真实验收命令
  - 写 `evaluation / reflection / change / review context`
  - 更新状态文件
  - 准备 commit / push

## Trial Result

- 两个 skill 的边界清晰，均对应高频、稳定、易遗漏的流程。
- `iteration-start-review` 直接对应 Phase 1 期间多次出现的主线分叉问题。
- `acceptance-closure` 直接对应每轮结束时固定重复的测试、文档闭环和状态同步流程。

## Ambiguities

- `iteration-start-review` 与 `AGENTS.md` 的边界仍需要保持清楚：
  - 它负责“如何执行开始前检查”
  - `AGENTS.md` 负责“必须遵守哪些全局规则”
- `acceptance-closure` 不应替代 runbook 和测试文件，只应组织固定收口工序。

## Conclusion

- 两个 skill 已具备最小试运行证据，可进入 active 状态。
