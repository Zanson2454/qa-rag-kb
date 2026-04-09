# Iter-024 Retrieval Readiness Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Phase 1 完成后，为知识库进入检索层建立一个最小可执行的 retrieval-readiness 基线，产出稳定 chunk corpus、corpus manifest、seed eval set 和交接 runbook，而不直接实现 embedding、vector DB 或 Retriever。

**Architecture:** 保持现有 importer 和 normalized knowledge 作为唯一上游输入，新建一个独立的 retrieval-prep slice 读取 `docs/knowledge/normalized/`，按确定性规则导出面向检索的 chunks 与评测基线。该 slice 只负责“为检索做准备”，不与 Phase 1 importer 逻辑耦合，也不把 loop 再扩成新的自治链路。

**Tech Stack:** Python 3.11、标准库 `pathlib/json/unittest`、PyYAML、现有 `docs/knowledge` / `src` / `tests` / `harness`

---

### Task 1: 固化 retrieval-ready 输出 contract

**Files:**
- Review: `docs/knowledge/README.md`
- Review: `docs/knowledge/examples/imported-defect-example.yaml`
- Review: `docs/knowledge/examples/imported-testcase-example.yaml`
- Create: `docs/knowledge/retrieval/README.md`
- Create: `docs/knowledge/schemas/retrieval-chunk.schema.yaml`
- Create: `docs/knowledge/schemas/retrieval-eval.schema.yaml`

- [ ] **Step 1: review 当前 normalized 记录的真实字段边界**
  - 明确以现有 `id`、`record_type`、`display_title`、`content_text`、`quality_flags`、`source`、`version` 为 retrieval-prep 输入，不再回写 Phase 1 schema。
- [ ] **Step 2: 定义 retrieval chunk 的最小 schema**
  - 至少包含：
    - `chunk_id`
    - `record_id`
    - `record_type`
    - `chunk_type`
    - `title`
    - `content_text`
    - `metadata`
    - `relation_refs`
    - `quality_flags`
- [ ] **Step 3: 定义 retrieval eval item 的最小 schema**
  - 至少包含：
    - `query_id`
    - `query`
    - `intent`
    - `expected_record_ids`
    - `expected_chunk_ids`
    - `notes`
- [ ] **Step 4: 在 `docs/knowledge/retrieval/README.md` 明确本阶段边界**
  - 包括：
    - 本阶段只做 chunk/export/eval baseline
    - 不实现 embedding / vector DB / retriever / QA generation
    - 后续检索层只能消费该阶段稳定产物

### Task 2: 先写 retrieval export 的失败测试

**Files:**
- Create: `tests/test_retrieval_export.py`
- Test: `docs/knowledge/examples/imported-defect-example.yaml`
- Test: `docs/knowledge/examples/imported-testcase-example.yaml`

- [ ] **Step 1: 为 defect 记录导出 summary / steps / expectation chunk 写失败测试**
  - 断言：
    - chunk ID 稳定
    - chunk type 可预测
    - chunk 内容不依赖 Excel 上下文
- [ ] **Step 2: 为 testcase 记录导出 summary / preconditions / steps chunk 写失败测试**
  - 断言 chunk 顺序和结构稳定。
- [ ] **Step 3: 为 relation / source / quality flag 透传写失败测试**
  - 断言 export 后仍保留 record 级关系与质量痕迹。
- [ ] **Step 4: 为 corpus manifest 写失败测试**
  - 至少断言：
    - `record_count`
    - `chunk_count`
    - `record_type_distribution`
    - `chunk_type_distribution`
- [ ] **Step 5: 运行 `python3 -m unittest tests/test_retrieval_export.py -v`，确认先失败**

### Task 3: 实现确定性的 retrieval corpus export

**Files:**
- Create: `src/qa_kb_retrieval/__init__.py`
- Create: `src/qa_kb_retrieval/__main__.py`
- Create: `src/qa_kb_retrieval/exporter.py`
- Modify: `tests/test_retrieval_export.py`

- [ ] **Step 1: 实现读取 normalized defects / testcases 的最小 loader**
- [ ] **Step 2: 为 defect 实现 section-based chunking**
  - 推荐最小 chunk type：
    - `summary`
    - `steps`
    - `expectation`
- [ ] **Step 3: 为 testcase 实现 section-based chunking**
  - 推荐最小 chunk type：
    - `summary`
    - `preconditions`
    - `steps`
- [ ] **Step 4: 定义稳定 `chunk_id` 规则**
  - 例如：`DEF-824380#summary`、`TC-1735078#steps`
- [ ] **Step 5: 导出 retrieval corpus 与 manifest**
  - 目标目录建议：
    - `docs/knowledge/retrieval/chunks/`
    - `docs/knowledge/retrieval/manifests/`
- [ ] **Step 6: 提供最小 CLI**
  - Run: `PYTHONPATH=src python3 -m qa_kb_retrieval --knowledge-root docs/knowledge`
- [ ] **Step 7: 重新运行 `python3 -m unittest tests/test_retrieval_export.py -v`**

### Task 4: 建立 seed eval set 与交接文档

**Files:**
- Create: `docs/knowledge/retrieval/eval-set.yaml`
- Modify: `docs/knowledge/retrieval/README.md`
- Modify: `README.md`

- [ ] **Step 1: 选取 8 到 12 条 seed queries**
  - 覆盖：
    - defect 症状查找
    - testcase 流程查找
    - defect/testcase 关系型查找
    - 质量风险或 known limitation 场景
- [ ] **Step 2: 为每条 query 明确 expected record/chunk**
- [ ] **Step 3: 在 README 中补当前项目阶段**
  - 从“Phase 1 MVP”推进为“Phase 2 Retrieval Readiness”
- [ ] **Step 4: 在 retrieval README 中写清 handoff 条件**
  - 只有当 export 和 eval baseline 稳定后，才进入真正 retriever 实验

### Task 5: 完成本轮验证与交接

**Files:**
- Modify: `tests/test_retrieval_export.py`
- Create: `harness/changes/iter-025-change.md`
- Create: `harness/evaluations/iter-025-eval.md`
- Create: `harness/reflections/iter-025-reflection.md`
- Create: `harness/review-contexts/iter-026-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 运行 `python3 -m unittest tests/test_retrieval_export.py -v`**
- [ ] **Step 2: 运行 `ruff format --check .`**
- [ ] **Step 3: 运行 `ruff check .`**
- [ ] **Step 4: 运行 `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`**
- [ ] **Step 5: 运行 retrieval export CLI 进行真实验收**
  - Run: `PYTHONPATH=src python3 -m qa_kb_retrieval --knowledge-root /tmp/qa-kb-retrieval-check`
- [ ] **Step 6: 在 evaluation 中明确 Phase 2 当前只签收到 retrieval-readiness，不外推为完整 RAG 闭环**
