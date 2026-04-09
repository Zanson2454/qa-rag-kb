# Project Goal
构建一个 QA 知识库系统（后续用于 RAG），支持缺陷和测试用例的结构化管理、导入、检索与评测。

# Working Mode
- 每次开始工作必须先 review 最近一轮 change record，再进入本轮 plan
- 必须先生成 plan，再进行实现
- 每轮必须有 evaluation 和 reflection
- 每轮必须生成 change record
- 下一轮必须先 review 上一轮改动

# Required Outputs
- exec plan
- evaluation
- reflection
- change record
- review context

# Rules
- 不允许跳过 plan 直接实现
- 不允许无评测进入下一阶段
- 不允许输出无结构内容
- 不允许忽略 change record
- 不允许跳过最近一轮 change record review 直接开始新一轮工作
- 不允许保留仅用于调试或实验的一次性测试文件到本轮结束
- 不允许只做临时验证而不沉淀正式验收测试或测试场景
- 项目内 skill 的新增、变更和废弃必须遵循 `docs/governance/skill-management.md`
- 同一 iteration 不允许并行推进两个不同主题的主线
- 若发现 `task-state.json` 与当前实现主线冲突，必须先停机并请求人工确认
- `task-state.json` 是当前确认主线的唯一状态源
- 非当前确认主线，不得覆盖状态文件
- 当用户询问某阶段是否完成时，必须显式对照对应 plan 的 `done_criteria`
- 不能只根据最近一轮实现进度判断阶段是否完成
- governance/documentation 主线与 implementation 主线不得共用 iteration 编号
- 若确需并行，必须先由人工指定主线和独立编号

# Git Rules
- 每轮必须说明改动文件
- 必须记录改动意图和风险
- 必须记录未解决问题
- 只要本轮有代码或配置改动，且测试与验收通过，结束前必须提交并推送到远程仓库
- 每次开始工作前必须先查看最近一轮 change record，并在本轮输出中说明 review context

# Test & Baseline Rules
- 过程中新增的临时调试测试、实验性测试文件、一次性验证脚本，必须在结束前删除或收敛到正式测试集中
- 每轮结束时必须保留针对目标结果的正式测试用例或测试场景，不允许只留下人工口头结论
- 每轮必须明确验收标准，且 evaluation 需要基于这些标准给出通过或失败结论
- 当一轮验收通过后，该轮沉淀的正式测试用例或测试场景即作为第一版回归基线，后续迭代必须优先回归这套基线
- 若本轮改动影响既有基线，必须同步更新基线测试和对应验收标准，并在 change record 中说明原因与风险

# Definition of Done
- 目标产物完成
- evaluation 通过
- change record 完整
- review context 完整
- 最近一轮 change record 已 review
- 临时测试已收敛，只保留正式回归测试
- 已形成可复用的验收测试/测试场景基线
- 若本轮有代码或配置改动，相关测试通过且已推送远程仓库
