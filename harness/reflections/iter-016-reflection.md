# Iter 016 Reflection

artifact:
  id: iter-016-reflection
  type: reflection
  stage: reviewing
  status: approved

## 本轮最重要的发现

- 在已有治理规则后，主线切换本身也应该作为独立 iteration 收口，而不是直接覆盖到下一条实现线。
- 这样可以避免“治理线结论”和“实现线执行结果”出现在同一轮文档里，降低状态歧义。
- 对于已有但未执行的计划，最安全的做法是先把状态切回，再进入真正实现。

## 后续观察点

- 下一轮执行 `ruff format` 基线计划时，是否还需要把旧计划重编为新的 iteration 编号。
- `task-state.json` 的主线切换规则在真实迭代中是否足够稳定。
