# Fixed Template Importer Runbook

本 runbook 说明如何运行当前仓库中的“固定模板版最小 Excel 导入器”。

## 如何运行最小导入器

在仓库根目录执行：

```bash
PYTHONPATH=src python3 -m qa_kb_importer --defect-limit 20 --testcase-limit 20
```

如果需要调整最小验证批次，可显式传参：

```bash
PYTHONPATH=src python3 -m qa_kb_importer \
  --defect-file input/issue-export-20260408.xlsx \
  --testcase-file input/测试用例-scm-20260408.xlsx \
  --knowledge-root docs/knowledge \
  --defect-limit 20 \
  --testcase-limit 20
```

## 当前支持的输入限制

- 只支持 `input/issue-export-20260408.xlsx`
- 只支持 `input/测试用例-scm-20260408.xlsx`
- 只支持固定 Sheet：
  - defect: `issue`
  - testcase: `测试用例.xlsx`
- defect 固定使用第 3 行表头
- testcase 固定使用第 1、2 行组合表头
- testcase 固定使用“首行有 `用例编号`，后续空 `用例编号` 行继续归并”的规则

## 输出位置

- 原始 Excel 归档到：
  - `docs/knowledge/imports/raw/defects/`
  - `docs/knowledge/imports/raw/testcases/`
- 批次摘要输出到 `docs/knowledge/imports/manifests/`
- 独立错误清单输出到 `docs/knowledge/imports/errors/`
- 批次质量报告输出到 `docs/knowledge/imports/reports/`
- validation 明细输出到 `docs/knowledge/imports/reports/`
- 规范化知识输出到：
  - `docs/knowledge/normalized/defects/`
  - `docs/knowledge/normalized/testcases/`
- 原始快照输出到：
  - `docs/knowledge/snapshots/defects/`
  - `docs/knowledge/snapshots/testcases/`
- 每条知识对象一个 YAML 文件，文件名使用 `<id>.yaml`

## 如何查看 validation / report / gate

- CLI 结束后会打印：
  - `batch=<batch-id>`
  - `errors=<count>`
  - `gate=<passed|warning|failed>`
  - `warnings=<count>`
  - `semantic_warnings=<count>`
  - `warning_rate=<ratio>`
  - `report=<report-path>`
- 批次报告文件：
  - `docs/knowledge/imports/reports/<batch-id>-report.yaml`
  - 适合回答“这一批整体质量怎么样”
- validation 明细文件：
  - `docs/knowledge/imports/reports/<batch-id>-validation-details.yaml`
  - 适合查看“哪条 normalized 记录失败了、报了什么错、有哪些 warning”
- gate 规则当前最小版本：
  - `failed`
    - 存在 schema 校验失败
    - 或存在导入错误记录
    - 或 `blocking_warning_rate > 0.30`
  - `warning`
    - schema 无失败、导入错误为 0
    - 且 `admissible_warning_rate > 0.10`
  - `passed`
    - 上述问题都没有

## Admission Policy

- `admissible`
  - 当前 warning 可接受，不阻断 Phase 1 收录，但会进入报告摘要。
  - 当前典型例子：
    - defect `missing_expected`，且 `expected_source_section=缺陷描述*`
- `blocking`
  - 当前 warning 会阻断收录或直接推高 gate 到 `failed`。
  - 当前典型例子：
    - defect `missing_expected`，且 `expected_missing_unrecoverable`
    - `missing_actual`
    - `missing_steps`

## 中等批次验收建议

- Phase 1 当前默认先跑 `20 defect + 20 testcase`。
- 样本选取规则固定为按源文件原始顺序截取前 N 条有效记录，保证结果可复现。
- 重点看 3 个字段：
  - `gate`
  - `admission_distribution`
  - `warning_code_distribution`
  - `failed_reason`
- 当前可接受的结论：
  - `passed`：可直接作为 Phase 1 验收证据。
  - `warning`：可继续保留样本，但要评估 warning 是否主要来自 `admissible` 噪声。
  - `failed`：先收敛 `blocking` warning，再考虑进入下一阶段。

## 已知限制

- 当前不支持未知模板或表头顺序变化。
- 当前不做全量生产导入，建议先跑 `20 defect + 20 testcase` 的中等批次验收。
- defect 的 `内容` 解析依赖 Markdown 风格段标题，如 `### 重现步骤`。
- testcase 的 `expected` 当前聚合为一个多行字符串，不是结构化步骤对象。
- 当前会输出独立错误清单、validation 明细和批次报告，但 source 定位仍主要停留在字段名和 section 级。
- 当前运行方式依赖 `PYTHONPATH=src`，还没有仓库级打包配置。

## 后续扩展点

- 增加错误记录清单输出，落到专门的导入批次目录。
- 增加导入器回归测试，覆盖更多真实脏数据样例。
- 补充版本比对和重复导入冲突处理。
- 将固定模板逻辑逐步抽象为可配置映射，但前提是先稳定回归测试。
