# Iter 015 Reflection

artifact:
  id: iter-015-reflection
  type: reflection
  stage: reviewing
  status: approved

## 本轮最重要的发现

- 最适合首先沉淀的 skill 不是业务逻辑 skill，而是“开始一轮”和“结束一轮”这两类流程 skill。
- `AGENTS.md` 与项目内 skill 的职责可以清楚分层：
  - `AGENTS.md` 负责全局硬规则
  - skill 负责高频稳定工作流
- 先沉淀最小 skill，比一开始抽象大量 skill 更稳妥。

## 后续观察点

- 需要在未来 2 到 3 轮真实迭代里继续判断这两个 skill 是否确实减少遗漏和返工。
- 若效果稳定，再考虑第三个 skill，如 `import-quality-tuning`。
