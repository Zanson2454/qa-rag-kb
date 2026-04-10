# Iter 025 Change Record

artifact:
  id: iter-025-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

基于已确认的 `测试知识问答台 v1` 设计稿，生成正式实现计划，并将当前主线从“retrieval-readiness 规划”切到“面向测试人员的问答产品实现”。

## 新增/修改文件

- `docs/exec-plans/active/iter-025-test-knowledge-qa-v1-plan.md`
- `harness/changes/iter-025-change.md`
- `harness/evaluations/iter-025-eval.md`
- `harness/reflections/iter-025-reflection.md`
- `harness/review-contexts/iter-026-context.md`
- `orchestrator/state/task-state.json`

## 改动结果

- 将上一轮 retrieval-ready 主线并入产品主线，不再作为孤立目标继续推进。
- 创建了 `测试知识问答台 v1` 的正式实现计划，明确：
  - React 前端
  - FastAPI 后端
  - retrieval chunks/export
  - citation-first 问答链路
- 保留第一期边界：
  - 只基于现有缺陷与用例
  - 必须附引用来源
  - 不接入 PRD、详设和自动化平台
- 将状态文件推进到 Iter-025 planning 完成状态。

## 风险

- 这是第一次同时引入前端、后端和问答链路，任务跨度明显大于前几轮 importer 调优。
- retrieval export、后端问答 API 和前端体验需要联动设计，若实现时切分不好，容易相互阻塞。
- 模型调用会引入环境变量与依赖配置问题，测试必须依赖 fake client，而不能把真实模型调用写死到回归链路里。

## 未解决问题

- 真实模型服务的最终 provider 还未定稿，只在计划中保留受控抽象层。
- retrieval chunk 粒度是否需要在第一次真实问答后再调，目前仍待实现验证。
- 是否要把问答 API 纳入 loop business gate，当前暂未决定。
