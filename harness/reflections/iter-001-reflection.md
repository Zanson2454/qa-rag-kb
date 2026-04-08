# Iter 001 Reflection

artifact:
  id: iter-001-reflection
  type: reflection
  stage: reviewing
  status: approved

## 本轮发现的问题

- 计划中的目录结构比本轮要求更完整，但本轮只允许实现最小骨架，导致目录暂时存在“计划视角”和“实现视角”的落差。
- `testcase` 在计划里偏向统一标题字段，本轮要求使用 `name`，需要后续导入时明确映射。
- 目前 schema 是“可读性优先”的 YAML 定义，人工维护友好，但机器严格校验能力有限。

## root causes

- 用户本轮明确要求“最小实现”，因此必须主动延后导入批次、快照和 manifest 目录。
- 上一轮 plan 是系统级设计，本轮则是最小落地，抽象层级不同。
- 当前仓库没有真实 Excel 样本，字段命名只能先按 plan 和人工示例折中。

## 下一轮建议改进项

- 以 Excel 导入能力为中心，补 `imports/raw/`、`imports/manifests/` 和字段映射模板。
- 固化 `id`、`name/title`、`source` 的映射规则，减少 schema 与计划之间的语义漂移。
- 增加受控词表文件，先覆盖 `severity`、`priority` 和常见状态值。
