# Iter 019 Reflection

artifact:
  id: iter-019-reflection
  type: reflection
  stage: reviewing
  status: approved

## 本轮最重要的发现

- 对 harness/loop 最稳的做法是：CLI 返回码负责控制信号，report/stdout 负责解释证据。
- 单独的 loop `knowledge_root` 能显著降低“重跑导致冲突”的假失败噪声。
- 当前主线已经不再是 gate 传播链路问题，而是 importer 质量层 warning 是否还要继续优化。

## 后续观察点

- `gate=warning` 是否已经满足当前阶段的可接受基线。
- 若继续优化 importer 质量层，应该优先分析 warning 来源，而不是继续改 loop 基础设施。
