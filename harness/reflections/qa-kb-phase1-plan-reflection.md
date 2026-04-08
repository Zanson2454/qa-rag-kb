# QA KB Phase 1 Plan Reflection

artifact:
  id: qa-kb-phase1-plan-reflection
  type: reflection
  stage: reviewing
  status: approved

reflection:
  root_causes:
    - 当前仓库只有目录骨架，没有现成 schema、样本或导入约定，因此计划必须先把边界收紧到 MVP 基础层。
    - whitepaper v1/v2 提供的是工程控制框架，不直接提供 QA 领域模型，需要额外把计划落到 defect/testcase 的数据设计上。
    - 如果目录结构不与现有仓库对齐，计划会变成“另起一套”，降低后续执行一致性。
  fix_strategy:
    - 采用“文件系统知识库”作为 MVP 主方案，减少 Phase 1 的实现依赖。
    - 用统一 schema 明确公共字段和类型扩展，保证后续导入和 RAG 共用一套基础模型。
    - 在计划中显式加入批次、快照、词表、冲突处理和可验证 done criteria，避免后续实现跑偏。
