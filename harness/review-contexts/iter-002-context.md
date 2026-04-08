# Iter 002 Review Context

artifact:
  id: iter-002-context
  type: review-context
  stage: reviewing
  status: approved

## 当前已完成内容

- 已创建最小知识库目录结构：
  - `docs/knowledge/defects/`
  - `docs/knowledge/testcases/`
  - `docs/knowledge/schemas/`
  - `docs/knowledge/examples/`
- 已落地两份最小统一 schema：
  - `docs/knowledge/schemas/defect.schema.yaml`
  - `docs/knowledge/schemas/testcase.schema.yaml`
- 已新增两条示例知识：
  - `docs/knowledge/examples/defect-example.yaml`
  - `docs/knowledge/examples/testcase-example.yaml`
- 已补 `docs/knowledge/README.md`，可指导手工新增知识。
- 已完成本轮 change / evaluation / reflection 闭环。

## 未解决问题

- Excel 导入目录、批次 manifest、原始快照目录尚未创建。
- 字段映射规则尚未落地，尤其是 `testcase.name` 与计划通用标题语义之间的映射。
- 受控词表和数据质量校验规则仍未文件化。

## 下一轮优先事项

- 优先补 Phase 1 的 Excel 导入基础能力，但仍保持最小范围。
- 先落目录与文档，不做复杂解析：
  - `docs/knowledge/imports/raw/`
  - `docs/knowledge/imports/manifests/`
  - 字段映射模板
- 明确 Excel 列名到 schema 字段的映射规则，尤其是缺陷步骤、预期/实际结果、测试用例前置条件和步骤。
- 设计最小导入 manifest 格式，至少记录批次、文件名、记录数和异常摘要。
