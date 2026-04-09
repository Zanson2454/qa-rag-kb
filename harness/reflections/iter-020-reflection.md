# Iter 020 Reflection

artifact:
  id: iter-020-reflection
  type: reflection
  stage: reviewing
  status: approved

## 本轮反思

- 这轮最重要的不是继续改代码，而是先验证“问题是否仍然存在”。
- 重新验收后可以确认，Iter-019 修复的是有效链路，而不是一次性碰巧通过。
- 这样避免了把主线继续耗在已经闭环的 gate 传播问题上。

## 经验

- 当当前代码、测试、状态文件和上一轮 review context 都指向“已解决”时，优先做复验比直接重开实现更稳。
- 对 loop 这类编排层，控制信号和证据信号必须分别验收：退出码决定停机，report/stdout 负责解释。

## 下一步建议

- 回到 importer 质量层，拆出当前 `warnings=3` 的来源。
- 判断这些 warning 是当前阶段可接受噪声，还是还需要继续收敛。
