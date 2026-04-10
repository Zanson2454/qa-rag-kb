# Iter-025 Test Knowledge QA V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于现有缺陷与用例知识，落地一个面向测试人员的测试知识问答台 v1，提供 React 前端、FastAPI 后端、最小检索链路、受控生成回答和可点击引用来源。

**Architecture:** 将上一轮 retrieval-readiness 目标收编为产品基础能力，而不是继续作为独立主线。实现上分为三层：`src/qa_kb_retrieval` 负责稳定 chunk/export 基线；`backend/app` 负责读取知识与 chunks、执行检索和问答编排；`frontend/` 负责对话页、引用区和详情抽屉。回答链路坚持“检索优先、生成受控、无引用不做肯定式回答”。

**Tech Stack:** Python 3.11、FastAPI、PyYAML、标准库 `unittest/pathlib/json`、Node.js 25、npm 11、React、TypeScript、Vite、Vitest

---

### Task 1: 固化 retrieval-ready 基线并写失败测试

**Files:**
- Review: `docs/superpowers/specs/2026-04-10-test-knowledge-qa-v1-design.md`
- Create: `docs/knowledge/retrieval/README.md`
- Create: `docs/knowledge/schemas/retrieval-chunk.schema.yaml`
- Create: `docs/knowledge/schemas/retrieval-eval.schema.yaml`
- Create: `tests/test_retrieval_export.py`

- [ ] **Step 1: 将设计稿里的问答输入约束映射成 retrieval artifact contract**
  - 明确第一期只消费 `docs/knowledge/normalized/` 下的 defect / testcase。
- [ ] **Step 2: 为 retrieval chunk schema 写最小文档**
  - 至少包含 `chunk_id`、`record_id`、`record_type`、`chunk_type`、`content_text`、`metadata`、`quality_flags`。
- [ ] **Step 3: 为 retrieval eval schema 写最小文档**
  - 至少包含 `query_id`、`query`、`expected_record_ids`、`expected_chunk_ids`。
- [ ] **Step 4: 在 `tests/test_retrieval_export.py` 里写 defect/testcase chunking 失败测试**
  - 覆盖 stable `chunk_id`、固定 `chunk_type`、record metadata 透传、manifest 统计。
- [ ] **Step 5: 运行 `python3 -m unittest tests/test_retrieval_export.py -v`，确认先失败**

### Task 2: 实现 retrieval export CLI，生成产品可消费的 chunks

**Files:**
- Create: `src/qa_kb_retrieval/__init__.py`
- Create: `src/qa_kb_retrieval/__main__.py`
- Create: `src/qa_kb_retrieval/exporter.py`
- Modify: `tests/test_retrieval_export.py`
- Create: `docs/knowledge/retrieval/eval-set.yaml`

- [ ] **Step 1: 实现 normalized record loader**
  - 读取 `docs/knowledge/normalized/defects/` 和 `docs/knowledge/normalized/testcases/`。
- [ ] **Step 2: 为 defect 实现最小 section-based chunking**
  - 推荐 `summary`、`steps`、`expectation` 三类。
- [ ] **Step 3: 为 testcase 实现最小 section-based chunking**
  - 推荐 `summary`、`preconditions`、`steps` 三类。
- [ ] **Step 4: 实现稳定 `chunk_id` 规则**
  - 示例：`DEF-824380#summary`、`TC-1735078#steps`。
- [ ] **Step 5: 导出 `docs/knowledge/retrieval/chunks/` 与 `docs/knowledge/retrieval/manifests/`**
- [ ] **Step 6: 先补一版 8 到 12 条 seed eval set**
  - 只覆盖现有 defect / testcase 问答场景。
- [ ] **Step 7: 运行 `PYTHONPATH=src python3 -m qa_kb_retrieval --knowledge-root docs/knowledge`**
- [ ] **Step 8: 重新运行 `python3 -m unittest tests/test_retrieval_export.py -v`，确认通过**

### Task 3: 搭 FastAPI 只读知识 API 和记录详情接口

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/models.py`
- Create: `backend/app/repository.py`
- Create: `backend/app/api_records.py`
- Create: `tests/test_knowledge_api.py`
- Create: `requirements.txt`

- [ ] **Step 1: 在 `requirements.txt` 中补最小后端依赖**
  - 至少包含 `pyyaml`、`fastapi`、`uvicorn`。
- [ ] **Step 2: 为记录详情和基础健康检查写失败测试**
  - 覆盖：
    - `GET /api/health`
    - `GET /api/records/{record_id}`
- [ ] **Step 3: 实现 YAML repository**
  - 负责按 ID 读取 defect / testcase 原始 normalized 记录。
- [ ] **Step 4: 实现 FastAPI app 和 records endpoint**
  - 返回产品需要的完整记录详情。
- [ ] **Step 5: 运行 `python3 -m unittest tests/test_knowledge_api.py -v`，确认通过**

### Task 4: 实现 citation-first 问答 API

**Files:**
- Create: `backend/app/retrieval.py`
- Create: `backend/app/llm_client.py`
- Create: `backend/app/api_chat.py`
- Create: `tests/test_chat_api.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 为问答 API 写失败测试**
  - 覆盖：
    - 返回 `answer`
    - 返回 `citations`
    - 引用必须包含 record ID 和片段
    - 无引用时返回 insufficient evidence 风格响应
- [ ] **Step 2: 实现最小 retrieval service**
  - 先基于 retrieval chunks 做关键词 / 规则检索，不追求复杂排序。
- [ ] **Step 3: 实现受控回答生成器接口**
  - 通过 `llm_client.py` 封装真实模型调用，测试中用 fake client。
- [ ] **Step 4: 实现 `/api/chat`**
  - 输入用户问题，输出受控回答和引用卡片。
- [ ] **Step 5: 运行 `python3 -m unittest tests/test_chat_api.py -v`，确认通过**

### Task 5: 脚手架 React 前端并做页面骨架

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/components/SessionSidebar.tsx`
- Create: `frontend/src/components/ChatPanel.tsx`
- Create: `frontend/src/components/CitationPanel.tsx`
- Create: `frontend/src/components/RecordDrawer.tsx`
- Create: `frontend/src/__tests__/App.test.tsx`

- [ ] **Step 1: 用 Vite + React + TypeScript 建最小前端骨架**
- [ ] **Step 2: 写页面骨架失败测试**
  - 覆盖：
    - 左侧会话栏
    - 中间问答区
    - 右侧引用区
- [ ] **Step 3: 实现紧凑版三栏布局**
  - 贴合已确认的页面结构。
- [ ] **Step 4: 实现基础 API client**
  - 先约定 `/api/chat` 和 `/api/records/{id}`。
- [ ] **Step 5: 运行 `npm --prefix frontend install`**
- [ ] **Step 6: 运行 `npm --prefix frontend run test`，确认通过**

### Task 6: 接入真实问答交互、引用卡片和详情抽屉

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/ChatPanel.tsx`
- Modify: `frontend/src/components/CitationPanel.tsx`
- Modify: `frontend/src/components/RecordDrawer.tsx`
- Create: `frontend/src/__tests__/chat-flow.test.tsx`

- [ ] **Step 1: 为提交问题、展示答案、点击引用打开详情写失败测试**
- [ ] **Step 2: 接入真实 `/api/chat` 返回结构**
- [ ] **Step 3: 实现引用卡片点击后拉取记录详情**
- [ ] **Step 4: 默认使用右侧抽屉展示详情**
- [ ] **Step 5: 在 UI 中显式体现“无引用不输出肯定式结论”**
- [ ] **Step 6: 运行 `npm --prefix frontend run test`，确认通过**
- [ ] **Step 7: 运行 `npm --prefix frontend run build`，确认前端可构建**

### Task 7: 联调、文档和本轮闭环

**Files:**
- Modify: `README.md`
- Create: `backend/README.md`
- Create: `frontend/README.md`
- Create: `harness/changes/iter-026-change.md`
- Create: `harness/evaluations/iter-026-eval.md`
- Create: `harness/reflections/iter-026-reflection.md`
- Create: `harness/review-contexts/iter-027-context.md`
- Modify: `orchestrator/state/task-state.json`

- [ ] **Step 1: 在 README 中补当前产品方向和启动方式**
- [ ] **Step 2: 运行后端正式验证**
  - Run: `python3 -m unittest tests/test_retrieval_export.py tests/test_knowledge_api.py tests/test_chat_api.py -v`
- [ ] **Step 3: 运行前端正式验证**
  - Run: `npm --prefix frontend run test`
  - Run: `npm --prefix frontend run build`
- [ ] **Step 4: 运行仓库基线验证**
  - Run: `ruff format --check .`
  - Run: `ruff check .`
  - Run: `python3 -m unittest tests/test_orchestrator_v0.py tests/test_orchestrator_loop_runner.py -v`
- [ ] **Step 5: 运行真实联调**
  - Run: `uvicorn backend.app.main:app --reload`
  - Run: `npm --prefix frontend run dev`
- [ ] **Step 6: 在 evaluation 中明确第一期只签收到“缺陷 + 用例问答台 v1”**
