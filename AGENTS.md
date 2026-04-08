# Project Goal
构建一个 QA 知识库系统（后续用于 RAG），支持缺陷和测试用例的结构化管理、导入、检索与评测。

# Working Mode
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

# Git Rules
- 每轮必须说明改动文件
- 必须记录改动意图和风险
- 必须记录未解决问题

# Definition of Done
- 目标产物完成
- evaluation 通过
- change record 完整
- review context 完整