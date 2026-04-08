# Agent Harness Whitepaper v2 (Engineering Edition)

## 1. Purpose
This document defines a fully operational AI-driven engineering system with:
- Autonomous generation
- Structured evaluation
- Iterative self-repair
- State-controlled execution
- Git-based iteration memory

---

## 2. Core System Model

Goal → Plan → Design → Implement → Test → Evaluate → Reflect → Repair → Loop → Deliver

---

## 3. Artifact Spec

All artifacts must follow structured schema.

### Common Schema
artifact:
  id: string
  type: string
  stage: string
  status: draft|validated|failed|approved
  content: {}

---

### Plan Template
plan:
  goal: string
  steps:
    - name: string
      output: string
  done_criteria: []

---

### Evaluation Template
evaluation:
  passed: boolean
  score: number
  errors: []
  suggestions: []

---

### Reflection Template
reflection:
  root_causes: []
  fix_strategy: []

---

### Change Artifact
change:
  iteration: string
  commits: []
  files: []
  summary: string
  risks: []
  unresolved: []

---

### Continuation Packet
continuation:
  task_id: string
  commit_range: string
  last_change: string
  evaluation_summary: string
  unresolved: []
  next_focus: []

---

## 4. Evaluation Spec

### Evaluators
- schema
- rule
- lint
- test
- integration

### Order
Schema → Rule → Static → Runtime

---

## 5. Execution Protocol

### States
created → planning → designing → implementing → testing → reviewing → repairing → approved

### Rules
- No stage skipping
- Evaluation required before transition
- Repair loop allowed with limits

---

## 6. State Machine

Transitions enforced with:
- success conditions
- failure routing
- retry caps

---

## 7. Budget & Stop Policy

limits:
  max_iterations: 8
  max_retry: 3

stop_conditions:
  - repeated failure
  - critical error

---

## 8. Change Trace System

Each iteration must record:
- git diff
- affected modules
- evaluation results
- unresolved issues

---

## 9. Toolchain

Required:
- AI generator
- file system access
- command execution
- test runner
- evaluator engine
- state tracker

---

## 10. Example Flow (API Test Framework)

1. Generate plan
2. Evaluate plan
3. Generate client + schema
4. Run tests
5. Fix failures
6. Repeat until pass

---

## 11. Success Criteria

- ≥80% automation
- stable iteration loop
- decreasing error recurrence

---

## 12. Conclusion

This system enables AI to operate as a self-improving engineering agent under structured control.
