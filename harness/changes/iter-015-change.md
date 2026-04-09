# Iter 015 Change Record

artifact:
  id: iter-015-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

增强 `AGENTS.md` 的主线治理规则，并创建两个项目内 skill：`iteration-start-review` 与 `acceptance-closure`，把高频、稳定、易遗漏的流程沉淀为可复用规范。

## 新增/修改文件

- `docs/exec-plans/active/iter-015-agents-and-skills-governance-plan.md`
- `AGENTS.md`
- `skills/iteration-start-review/SKILL.md`
- `skills/acceptance-closure/SKILL.md`
- `tests/test_governance_assets.py`
- `tests/test_orchestrator_v0.py`
- `docs/governance/skill-trials/iter-015-skills-trial.md`
- `harness/changes/iter-015-change.md`
- `harness/evaluations/iter-015-eval.md`
- `harness/reflections/iter-015-reflection.md`
- `harness/review-contexts/iter-016-context.md`
- `orchestrator/state/task-state.json`

## 风险

- 若 skill 描述过宽，容易与 `AGENTS.md`、runbook 或 plan 模板重叠。
- 当前只做最小试运行记录，后续仍需在真实迭代中继续验证收益。
- 状态文件若被并行主线再次覆盖，新的主线治理规则仍需要靠执行纪律落实。

## 未解决问题

- 是否需要为 skill 增加附属 checklist/template，当前尚未证明有必要。
- 是否要为项目内 skill 增加索引文档，仍可观察后续数量增长再决定。
