# QA Knowledge Base Phase 1 MVP Exec Plan

artifact:
  id: qa-kb-phase1-plan
  type: plan
  stage: planning
  status: validated

## 1. goal

构建一个最小可用的 QA Knowledge Base 基础层，能够从 Excel 导入缺陷和测试用例，落地到统一 schema 和固定知识目录结构中，并具备基础可维护性，为后续 QA RAG 的切片、索引、检索与评测提供稳定输入。

## 2. in_scope（仅限 MVP）

- 支持 Excel 作为唯一输入源，覆盖 `defect` 和 `testcase` 两类数据。
- 定义统一知识 schema，包括公共字段和类型专属字段。
- 定义知识目录结构、命名规则、批次管理规则和版本保留规则。
- 定义导入流程：原始文件保存、字段映射、校验、规范化、落盘。
- 定义最小管理能力：可追溯来源、可识别批次、可发现重复、可人工修订。
- 定义 RAG-ready 输出要求，包括稳定 ID、结构化文本块、关联关系和元数据字段。
- 产出可执行的实施阶段划分、验收标准、风险清单和评测标准。

## 3. out_of_scope

- 不实现向量库、Embedding、Retriever、生成式问答链路。
- 不开发 Web UI、后台管理页面或审批流。
- 不接入除 Excel 之外的外部系统，如 Jira、禅道、TestRail 或数据库。
- 不处理附件二进制内容的自动解析，如截图、日志包、录屏。
- 不建设权限系统、租户隔离或审计平台。
- 不做自动知识清洗、自动摘要、自动标签生成。
- 不承诺 Phase 1 内实现增量同步或双向回写。

## 4. knowledge schema 设计（defect + testcase）

### 4.1 设计原则

- 统一使用“公共信封 + 类型扩展”模型，避免两类数据完全割裂。
- 原始 Excel 数据必须可追溯，规范化字段必须可验证。
- 每条知识记录必须有稳定 `kb_id`，并保留 `source_id` 与 `import_batch_id`。
- 记录既要适合人工维护，也要适合后续 RAG 切片，因此正文与元数据分离。

### 4.2 公共字段（两类记录共享）

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `kb_id` | string | 是 | 知识库主键，格式建议为 `DEF-<source_id>` 或 `TC-<source_id>` |
| `record_type` | enum | 是 | `defect` / `testcase` |
| `title` | string | 是 | 规范化标题 |
| `source_id` | string | 是 | 来源系统中的原始主键或唯一标识 |
| `source_file` | string | 是 | Excel 文件名 |
| `source_sheet` | string | 是 | Sheet 名称 |
| `source_row` | integer | 是 | Excel 原始行号 |
| `import_batch_id` | string | 是 | 一次导入任务的唯一批次号 |
| `status` | string | 是 | 规范化状态值 |
| `priority` | string | 否 | 优先级或紧急度 |
| `module` | string | 否 | 业务模块或功能域 |
| `tags` | string[] | 否 | 统一标签集合 |
| `owner` | string | 否 | 当前责任人 |
| `created_at` | string | 否 | 原始创建时间，ISO 8601 |
| `updated_at` | string | 否 | 原始更新时间，ISO 8601 |
| `source_status_raw` | string | 是 | Excel 原始状态值 |
| `raw_snapshot_path` | string | 是 | 对应原始行快照路径 |
| `content_text` | string | 是 | 提供给后续 RAG 的主文本 |
| `relation_refs` | string[] | 否 | 关联记录 ID，如 testcase 关联 defect |
| `quality_flags` | string[] | 否 | 数据缺失、字段冲突、重复疑似等标志 |
| `version` | integer | 是 | 规范化记录版本号 |

### 4.3 defect 专属字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `severity` | string | 否 | 严重程度 |
| `environment` | string | 否 | 发生环境 |
| `found_in_version` | string | 否 | 发现版本 |
| `fixed_in_version` | string | 否 | 修复版本 |
| `reproduction_steps` | string[] | 否 | 复现步骤，按顺序保留 |
| `expected_result` | string | 否 | 预期结果 |
| `actual_result` | string | 否 | 实际结果 |
| `root_cause` | string | 否 | 根因说明，若源表存在 |
| `resolution` | string | 否 | 修复结论 |
| `linked_testcases` | string[] | 否 | 关联测试用例 ID |

### 4.4 testcase 专属字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `testcase_type` | string | 否 | 功能、回归、冒烟等 |
| `preconditions` | string[] | 否 | 前置条件 |
| `test_steps` | object[] | 否 | 每步包含 `step_no`、`action`、`expected` |
| `expected_summary` | string | 否 | 预期结果摘要 |
| `requirement_refs` | string[] | 否 | 关联需求标识 |
| `linked_defects` | string[] | 否 | 关联缺陷 ID |
| `execution_result` | string | 否 | 最近一次执行结果，若源表存在 |

### 4.5 规范化策略

- 状态、优先级、严重度采用受控词表，不保留自由发挥作为主字段。
- 所有多行文本统一转为数组或长文本，不依赖 Excel 单元格格式。
- `content_text` 由规范化字段拼接生成，建议顺序为标题、模块、状态、步骤/现象、预期/实际、关联关系。
- 无法稳定映射的字段不直接丢弃，进入 `raw_snapshot` 并打上 `quality_flags`。

## 5. directory structure

Phase 1 建议知识目录落在现有仓库的 `docs/knowledge/` 下，保持“原始输入、规范化输出、字典规则、批次记录”分层：

```text
docs/knowledge/
├── imports/
│   ├── raw/
│   │   ├── defects/
│   │   └── testcases/
│   └── manifests/
├── normalized/
│   ├── defects/
│   └── testcases/
├── snapshots/
│   ├── defects/
│   └── testcases/
├── taxonomies/
│   ├── status-map.yaml
│   ├── priority-map.yaml
│   └── severity-map.yaml
└── README.md
```

目录职责：

- `imports/raw/`：保存原始 Excel，按批次归档，禁止覆盖。
- `imports/manifests/`：记录每次导入的批次元数据、输入文件、记录数、异常摘要。
- `normalized/`：保存统一 schema 后的标准知识记录，建议一条记录一个文件。
- `snapshots/`：保存逐行原始结构化快照，便于追溯与人工核对。
- `taxonomies/`：保存受控词表和映射规则，避免状态名和优先级漂移。

## 6. data import strategy

### 6.1 输入假设

- 每次导入至少提供一个 Excel 文件。
- 单个文件可以只包含 `defect`、只包含 `testcase`，或按不同 Sheet 混合。
- 列名可能不一致，因此必须通过映射规则而不是列序号做解析。

### 6.2 导入流程

1. 接收 Excel 并生成 `import_batch_id`。
2. 将原始文件归档到 `docs/knowledge/imports/raw/<type>/`。
3. 读取 Sheet 元数据，确认文件类型、列名、记录数和空值情况。
4. 按字段映射规则将 Excel 列映射到统一 schema。
5. 执行规则校验：
   - 必填字段缺失
   - 主键冲突或缺失
   - 状态/优先级/严重度不在词表
   - 长文本为空但核心字段缺失
6. 生成逐行 `snapshot`，保留原始值与规范化值对照。
7. 输出规范化记录到 `normalized/defects` 或 `normalized/testcases`。
8. 生成批次 `manifest`，记录成功数、失败数、警告数、重复疑似数。
9. 对失败记录不落标准库，只进入异常清单，等待人工处理。

### 6.3 重复与覆盖策略

- 同一 `kb_id` 再次导入时，不直接覆盖，优先比较 `updated_at` 和批次来源。
- 如果来源相同且内容一致，仅更新 `manifest` 引用，不新增版本。
- 如果来源相同但内容变化，记录为 `version + 1`。
- 如果不同来源映射到同一 `kb_id`，标记为冲突并进入人工复核。

### 6.4 RAG 准备约束

- 每条记录必须可独立切片，不依赖 Excel 上下文。
- 文本字段需要包含足够语义信息，避免仅保存代码式枚举值。
- 缺陷与用例之间的关系必须显式保存，后续检索才能做关联召回。

## 7. steps（必须分阶段）

### Phase 0. 基线确认

- 明确缺陷与测试用例的 Excel 样本范围。
- 确认 MVP 仅支持人工触发导入，不做自动同步。
- 确认知识库存储以文件系统为准，不引入数据库。
- 输出：范围确认记录、样本清单、约束清单。

### Phase 1. 统一 schema 定稿

- 梳理白皮书要求与 MVP 最小字段集。
- 定义公共字段、类型专属字段、受控词表和主键规则。
- 明确 `content_text` 的拼接规范和 `quality_flags` 规则。
- 输出：schema 文档、字段映射规则、词表初稿。

### Phase 2. 目录与命名规范定稿

- 设计 `docs/knowledge/` 的目录树。
- 明确文件命名、批次命名、版本号和保留策略。
- 明确 raw、snapshot、normalized、manifest 各自职责。
- 输出：目录规范、命名规范、版本策略。

### Phase 3. 导入策略与校验规则定稿

- 为 `defect` 和 `testcase` 分别建立 Excel 列映射模板。
- 定义导入流程中的校验点、失败规则、冲突规则和异常输出。
- 定义最小人工修订流程和回溯流程。
- 输出：导入流程规范、校验规则、异常处理规范。

### Phase 4. MVP 验收方案定稿

- 选定至少一份缺陷样本和一份测试用例样本作为验收基线。
- 按 done criteria 逐条定义验证方式和预期结果。
- 明确后续进入 RAG Phase 2 前必须补齐的接口点。
- 输出：验收清单、样本基线、Phase 2 交接条件。

## 8. risks（至少列 5 个）

1. Excel 列名不稳定，导致同义字段无法可靠映射。
2. 原始数据缺少唯一主键，容易造成重复记录和误覆盖。
3. 缺陷与测试用例的状态体系不统一，统一 schema 后可能丢失语义。
4. 多行步骤、合并单元格、富文本内容在导入时容易失真。
5. 历史 Excel 质量不齐，必填字段大量缺失会降低知识库可用性。
6. 不同批次对同一记录的更新时间不可信，版本判断可能错误。
7. 关联关系字段缺失时，后续 RAG 无法做缺陷和用例联动召回。
8. 若 `content_text` 拼接规则设计过弱，后续检索质量会先天不足。
9. 若目录与命名规范不严格，人工维护阶段很快出现漂移。

## 9. done_criteria（必须可验证）

- 已存在一份经确认的统一 schema 文档，明确公共字段、`defect` 字段、`testcase` 字段、必填约束和词表规则。
- 已存在一份知识目录结构规范，明确 `imports/raw`、`imports/manifests`、`snapshots`、`normalized`、`taxonomies` 的职责。
- 已存在一份导入策略文档，覆盖批次生成、原始文件保存、字段映射、校验、冲突处理、版本策略和异常记录。
- 已定义至少一份缺陷 Excel 样本映射表和一份测试用例 Excel 样本映射表。
- 已定义批次 `manifest` 的最小字段集合，至少包含导入文件、记录数、成功数、失败数、警告数和时间戳。
- 已定义重复判定和覆盖策略，并给出冲突进入人工复核的条件。
- 已定义 `content_text` 生成规则，确保每条知识记录可作为后续 RAG 的独立输入。
- 已完成基于 whitepaper v2 Evaluation Spec 的自评，评测结果为 `passed: true`。

## Appendix. 推荐方案与取舍

### 推荐方案

采用“文件系统知识库 + Excel 批次导入 + 统一 schema + 受控词表 + 一条记录一个规范化文件”的方案。

### 对比方案 A：直接保留 Excel 作为主存储

- 优点：启动快。
- 缺点：不可审计、不可稳定切片、难做版本管理，不适合作为后续 RAG 基础。

### 对比方案 B：Phase 1 直接上数据库

- 优点：结构化能力强。
- 缺点：超出 MVP 范围，增加实现复杂度，也不利于早期人工校验与仓库内审阅。

### 选择理由

文件系统方案最符合当前仓库结构和 Phase 1“先打基础层”的目标，既能保持可追溯和可维护，又能为下一阶段引入索引或向量化留下稳定接口。
