from __future__ import annotations

from typing import Any


VALID_STATES = {
    "created",
    "planning",
    "implementing",
    "evaluating",
    "reflecting",
    "completed",
    "blocked",
    "failed",
}


def validate_state_payload(state: dict[str, Any]) -> None:
    required_keys = {
        "task_id",
        "current_iteration",
        "current_state",
        "current_goal",
        "last_outputs",
        "decision",
        "limits",
    }
    missing = sorted(required_keys - set(state.keys()))
    if missing:
        raise ValueError(f"task-state.json 缺少必填字段: {', '.join(missing)}")

    current_state = state["current_state"]
    if current_state not in VALID_STATES:
        raise ValueError(f"task-state.json 的 current_state 非法: {current_state}")

    limits = state["limits"]
    if not isinstance(limits, dict):
        raise ValueError("task-state.json 的 limits 必须是对象")
    for key in ("max_retry", "retry_count"):
        if key not in limits:
            raise ValueError(f"task-state.json 的 limits 缺少字段: {key}")
        if not isinstance(limits[key], int):
            raise ValueError(f"task-state.json 的 limits.{key} 必须是整数")

    current_plan = state.get("current_plan")
    if current_plan is not None:
        if not isinstance(current_plan, dict):
            raise ValueError("task-state.json 的 current_plan 必须是对象")
        for key in ("iteration", "path"):
            if key not in current_plan:
                raise ValueError(f"task-state.json 的 current_plan 缺少字段: {key}")
        if not isinstance(current_plan["iteration"], int):
            raise ValueError("task-state.json 的 current_plan.iteration 必须是整数")
        if not isinstance(current_plan["path"], str) or not current_plan["path"].strip():
            raise ValueError("task-state.json 的 current_plan.path 必须是非空字符串")
