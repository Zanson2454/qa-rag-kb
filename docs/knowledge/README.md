# QA Knowledge Base

`docs/knowledge/` 是 QA Knowledge Base 的基础层目录，用于以文件形式维护结构化缺陷知识和测试用例知识，为后续 Excel 导入、质量校验和 RAG 处理做准备。

## 目录用途

- `defects/`：保存正式缺陷知识，一条知识一个文件。
- `testcases/`：保存正式测试用例知识，一条知识一个文件。
- `schemas/`：保存当前生效的统一 schema，新增或调整字段时先更新这里。
- `examples/`：保存最小示例，供人工录入和后续导入实现参考。

## defect / testcase 基本规范

- `defect` 和 `testcase` 都必须有稳定 `id`、`content_text`、`quality_flags`、`source`、`version`。
- `defect` 关注缺陷现象，核心字段包括 `title`、`severity`、`steps`、`expected`、`actual`。
- `testcase` 关注验证流程，核心字段包括 `name`、`preconditions`、`steps`、`expected`、`priority`。
- `content_text` 必须是可直接阅读的完整文本，不能只保留零散字段值。
- `quality_flags` 用于记录缺失字段、格式异常、人工判断风险；没有问题时使用空数组。
- `source` 必须保留来源信息。当前手工新增可以使用 `manual`，后续 Excel 导入统一改为 `excel`。

## 如何新增一条知识

1. 先判断记录类型是 `defect` 还是 `testcase`。
2. 参考 `schemas/` 中对应 schema，准备完整字段。
3. 参考 `examples/` 中示例文件格式创建新文件。
4. 将正式知识落到：
   - `docs/knowledge/defects/`：缺陷知识
   - `docs/knowledge/testcases/`：测试用例知识
5. 手工检查 `content_text` 是否已经包含标题、模块、步骤和预期结果等核心语义。
6. 如有字段缺失或质量疑点，写入 `quality_flags`，不要静默省略。

## 后续 Excel 导入会落到哪里

- Phase 1 当前轮次还不实现 Excel 解析。
- 按已通过评测的计划，后续 Excel 原始文件会落到 `docs/knowledge/imports/raw/`。
- 后续导入生成的标准化知识会落到 `docs/knowledge/defects/` 和 `docs/knowledge/testcases/`。
- 如需保留批次信息、原始快照和导入清单，将在后续轮次补充 `imports/manifests/`、`snapshots/` 等目录。
