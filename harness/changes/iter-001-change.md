# Iter 001 Change Record

artifact:
  id: iter-001-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

基于 `docs/exec-plans/active/qa-kb-phase1-plan.md`，落地 QA Knowledge Base Phase 1 的最小骨架，包括知识目录、统一 schema、最小示例和人工维护说明文档，不实现 Excel 解析、RAG、搜索或 embedding。

## 新增/修改文件

- `docs/knowledge/README.md`
- `docs/knowledge/schemas/defect.schema.yaml`
- `docs/knowledge/schemas/testcase.schema.yaml`
- `docs/knowledge/examples/defect-example.yaml`
- `docs/knowledge/examples/testcase-example.yaml`
- `harness/changes/iter-001-change.md`
- `harness/evaluations/iter-001-eval.md`
- `harness/reflections/iter-001-reflection.md`
- `harness/review-contexts/iter-002-context.md`

## 每个改动对应的 plan step

- `docs/knowledge/schemas/defect.schema.yaml`
  - 对应 `Phase 1. 统一 schema 定稿`
- `docs/knowledge/schemas/testcase.schema.yaml`
  - 对应 `Phase 1. 统一 schema 定稿`
- `docs/knowledge/README.md`
  - 对应 `Phase 2. 目录与命名规范定稿`
- `docs/knowledge/examples/defect-example.yaml`
  - 对应 `Phase 3. 导入策略与校验规则定稿`
- `docs/knowledge/examples/testcase-example.yaml`
  - 对应 `Phase 3. 导入策略与校验规则定稿`
- `harness/evaluations/iter-001-eval.md`
  - 对应 `Phase 4. MVP 验收方案定稿`
- `harness/reflections/iter-001-reflection.md`
  - 对应本轮评测后反思闭环
- `harness/review-contexts/iter-002-context.md`
  - 对应下一轮交接上下文

## 风险

- 当前 schema 仍是文档型 YAML，还不是严格可执行校验器。
- 示例知识由人工构造，尚未覆盖真实 Excel 中的脏数据情况。
- 当前尚未落批次目录和导入 manifest，下一轮接入 Excel 时仍需补齐。
- `testcase` 使用 `name`，而上一轮 plan 的公共字段使用 `title`，后续导入设计需要显式做字段映射。

## 未解决问题

- 是否需要在下一轮将 `defects/` 和 `testcases/` 中的正式知识命名规则固定为 `<id>.yaml`。
- 是否需要把 `source` 从嵌套对象进一步拆成 plan 中的公共字段集合。
- Excel 列名映射表和受控词表文件尚未落地。
