# Iter 022 Change Record

artifact:
  id: iter-022-change
  type: change
  stage: reviewing
  status: approved

## 本轮目标

在 `20 defect + 20 testcase` 的中等批次上重新验证 Iter-021 的 defect `expected` 候选恢复规则，确认 importer 质量基线是否稳定。

## 新增/修改文件

- `docs/exec-plans/active/iter-022-medium-batch-stability-validation-plan.md`
- `harness/changes/iter-022-change.md`
- `harness/evaluations/iter-022-eval.md`
- `harness/reflections/iter-022-reflection.md`
- `harness/review-contexts/iter-023-context.md`
- `orchestrator/state/task-state.json`

## 改动结果

- 新增 Iter-022 验收计划，固定了中等批次规模、命令和判定标准。
- 运行了真实 importer 中等批次验收：
  - `PYTHONPATH=src python3 -m qa_kb_importer --knowledge-root /tmp/qa-kb-iter-022-check --defect-limit 20 --testcase-limit 20`
  - 结果：`gate=warning warnings=18 admissible_warnings=17 blocking_warnings=1 conflicts=0`
- 读取了中等批次 report/details，确认 warning 主要来自：
  - `missing_expected: 17`
  - `missing_actual: 1`
  - `testcase_steps_too_short: 1`
- 补跑了 importer 与 loop 回归测试，以及真实 loop：
  - importer 质量测试通过
  - orchestrator / loop 回归测试通过
  - `python3 orchestrator/run.py loop --root .` 仍返回 `loop iteration=22 ok=true stop_reason=none`

## 风险

- 当前 `expected` 候选恢复只在小批次样本上收敛到 `passed`，放大到中等批次后仍有大量 `missing_expected` 未覆盖。
- 剩余 warning 混有多种记录形态，包括 bundle 型问题单、接口报错类标题、以及疑似需求/问句型条目；若下一轮不先分类就扩规则，容易把启发式写得过宽。

## 未解决问题

- 还没有为标题直带期望语义的 defect 补 title-driven `expected` 恢复规则，例如：
  - `没保存上`
  - `未显示全`
  - `没有回显`
  - `报 500/404`
  - `过账后才允许`
- 还没有决定如何处理 `问题若干 / 问题集合 / 布局调整 / 需要产品确认` 这类 bundle 或需求式条目。
- `DEF-824272` 这类既缺 `expected` 又缺 `actual` 的问句型记录，是否应作为非 defect 提前拒收，还未定稿。
