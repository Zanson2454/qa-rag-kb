# Iter-012 Defect Expected Classification And Admission Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 判断 defect `missing_expected` 高占比究竟属于源模板长期噪声还是当前解析缺口，并把 warning 收录策略固化为可执行、可回归的 Phase 1 准入规则。

**Architecture:** 保持现有固定模板 importer 主流程不变。先在 `importer.py` 中补更明确的 defect `expected` 提取分类，再在 `validation.py` 与 `quality.py` 中把 warning 从“单一语义告警”升级为“可接受噪声 / 阻断 warning”两层策略。`import-runbook.md` 和 harness 文档负责沉淀本轮验收标准、判定依据和回归基线。

**Tech Stack:** Python 3.11、标准库 `unittest/pathlib/collections/re`、PyYAML、现有 `src/qa_kb_importer` / `tests` / `docs/knowledge` / `harness`

---

### Task 1: 先写 defect expected 分类与收录策略的失败测试

**Files:**
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `tests/test_validation_and_quality.py`

- [ ] **Step 1: 写 defect expected 提取分类测试**
  - 构造 3 类 defect 内容：
    - 有明确 `### 期望结果*`
    - 无 `期望结果` 段但可从其他段落推断
    - 完全缺失且不可恢复
  - 断言导入结果会输出明确分类，而不是只有空字符串。
- [ ] **Step 2: 写 warning detail 源定位测试**
  - 断言 `missing_expected` 相关 detail 至少补：
    - `source_field`
    - `source_section`
    - `admission`
- [ ] **Step 3: 写收录策略测试**
  - 断言 warning 至少分为：
    - `admissible`
    - `blocking`
  - 并验证 `missing_expected` 可根据分类落到不同 admission。
- [ ] **Step 4: 写 batch gate 与 admission 联动测试**
  - 断言 gate 不再把所有 `missing_expected` 一律算作阻断语义 warning。
  - 对“可接受噪声”只计入 admission 摘要，不直接推高阻断比例。
- [ ] **Step 5: 运行 `python3 -m unittest tests/test_validation_and_quality.py -v`，确认新测试先失败**

### Task 2: 在 importer 中补 defect expected 的最小分类能力

**Files:**
- Modify: `src/qa_kb_importer/importer.py`

- [ ] **Step 1: 定义 defect expected 缺失的最小分类闭集**
  - 本轮先固定：
    - `expected_section_present`
    - `expected_missing_but_description_present`
    - `expected_missing_unrecoverable`
- [ ] **Step 2: 在 defect normalize 结果中补分类元数据**
  - 至少补到 normalized 记录或 snapshot 可读字段，供 validation 使用。
- [ ] **Step 3: 若 `期望结果` 段缺失但存在描述性段落，显式标记为“可恢复但未恢复”**
  - 不要求本轮强行生成高置信 `expected` 文本。
- [ ] **Step 4: 让 snapshot 保留与 `expected` 判定相关的原始段落上下文**
  - 至少记录来源 section 名称，便于后续定位。

### Task 3: 把 validation / quality 扩展为 admission policy

**Files:**
- Modify: `src/qa_kb_importer/validation.py`
- Modify: `src/qa_kb_importer/quality.py`

- [ ] **Step 1: 扩展 warning detail 结构**
  - 至少包含：
    - `source_field`
    - `source_section`
    - `admission`
- [ ] **Step 2: 固定本轮最小 admission policy**
  - `admissible`
    - 源模板长期噪声，但不阻断 Phase 1 收录
  - `blocking`
    - 影响后续检索或语义完整性，阻断收录
- [ ] **Step 3: 为 `missing_expected` 接 admission 规则**
  - `expected_missing_but_description_present` => 暂定 `admissible`
  - `expected_missing_unrecoverable` => `blocking`
- [ ] **Step 4: 让 batch report 输出 admission 聚合**
  - 至少输出：
    - `admissible_warning_count`
    - `blocking_warning_count`
    - `admission_distribution`
- [ ] **Step 5: 调整 gate 规则**
  - 保持：
    - `schema_fail_count > 0` => `failed`
    - `error_count > 0` => `failed`
  - 新增：
    - `blocking_warning_rate > 0.30` => `failed`
    - `admissible_warning_rate > 0.10` 且未命中 `failed` => `warning`
    - 其他 => `passed`

### Task 4: 固化 runbook、验收标准和回归基线

**Files:**
- Modify: `docs/knowledge/import-runbook.md`
- Create: `harness/changes/iter-012-change.md`
- Create: `harness/evaluations/iter-012-eval.md`
- Create: `harness/reflections/iter-012-reflection.md`
- Create: `harness/review-contexts/iter-013-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 在 runbook 中新增 admission policy 解读**
  - 明确哪些 warning 允许收录，哪些 warning 阻断收录。
- [ ] **Step 2: 更新中等批次验收标准**
  - 明确本轮看的是 `blocking_warning_rate`，不是所有 semantic warning 的总和。
- [ ] **Step 3: 运行一次真实中等批次导入并记录 admission 分布**
  - 命令：
    - `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-012-check --defect-limit 20 --testcase-limit 20`
- [ ] **Step 4: 基于真实结果编写 change / evaluation / reflection**
  - 明确记录：
    - `missing_expected` 中哪些属于可接受噪声
    - 哪些仍然阻断收录
    - gate 是否从 `failed` 收敛到更贴近真实样本质量的结论
- [ ] **Step 5: 更新状态文件与下一轮 review context**
  - 若策略稳定，则下一轮评估是否已具备进入检索层准备工作的前提。
  - 若策略仍不稳定，则下一轮继续收敛 defect `expected` 提取。

### Task 5: 完成本轮验证闭环

**Files:**
- Modify: `tests/test_validation_and_quality.py`
- Modify: `tests/test_fixed_template_importer.py`
- Modify: `harness/evaluations/iter-012-eval.md`
- Modify: `harness/reflections/iter-012-reflection.md`
- Modify: `harness/changes/iter-012-change.md`
- Modify: `harness/review-contexts/iter-013-context.md`

- [ ] **Step 1: 运行 `python3 -m unittest tests/test_validation_and_quality.py -v`**
- [ ] **Step 2: 运行 `python3 -m unittest tests/test_fixed_template_importer.py tests/test_validation_and_quality.py -v`**
- [ ] **Step 3: 运行 `python3 -m unittest tests/test_orchestrator_v0.py -v`**
- [ ] **Step 4: 复核本轮没有留下临时调试测试或一次性验证脚本**
- [ ] **Step 5: 依据真实验证结果完成最终 evaluation / reflection / change record / review context**
