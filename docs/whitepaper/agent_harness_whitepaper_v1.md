# Agent Harness Whitepaper (v1.0)

## 1. Overview
This document defines an AI-first engineering system that enables:
- Autonomous artifact generation
- Automated evaluation
- Self-reflection and repair
- Controlled iteration loops
- Human final approval

---

## 2. Core Architecture
Goal → Generator → Evaluator → Reflector → Repair → State Machine → Budget Control → Loop → Human Gate

---

## 3. Artifact Spec
Defines all structured outputs.

### Common Fields
- id
- type
- stage
- status
- content

### Types
- Goal
- Plan
- Design
- Implementation
- Test
- Evaluation
- Reflection
- Delivery
- Change
- Review Context

---

## 4. Evaluation Spec
All outputs must be machine-evaluable.

### Evaluators
- Schema
- Rule
- Static
- Runtime
- Human Gate

### Output Format
- passed
- score
- errors
- suggestions

---

## 5. Execution Protocol

### States
created → planning → designing → implementing → testing → reviewing → repairing → approved

### Rules
- No skipping stages
- Mandatory evaluation before transition
- Retry limits enforced

---

## 6. State Machine
Defines valid transitions and prevents infinite loops.

---

## 7. Budget & Stop Policy
- Max iterations
- Max retries per stage
- Escalation rules

---

## 8. Change Trace Spec

### Change Artifact
- commit range
- changed files
- intent
- risks
- unresolved issues

### Review Context
- previous changes
- evaluation results
- next focus

### Continuation Packet
Standard input for next iteration.

---

## 9. Toolchain Definition

### Required
- AI generator
- file system ops
- command execution
- test runner
- evaluation engine
- state tracker

---

## 10. Success Criteria
- ≥80% tasks completed autonomously
- Stable evaluation loop
- Reduced repeated errors
- Minimal human intervention

---

## 11. Conclusion
This system transforms AI usage from prompt-based interaction into a structured, self-improving engineering system.
