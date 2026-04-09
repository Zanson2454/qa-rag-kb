from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from .validation import validate_state_payload


CommandRunner = Callable[[list[str], Path, dict[str, str] | None], dict[str, Any]]


def run_local_loop(root: Path, command_runner: CommandRunner | None = None) -> dict[str, Any]:
    runner = command_runner or _default_command_runner
    state = _load_state(root)
    iteration = int(state["current_iteration"])

    context = _load_context(root, state)
    if context["stop_reason"]:
        return {
            "ok": False,
            "iteration": iteration,
            "plan_path": context["plan_path"],
            "fast_gates": [],
            "business_gate": None,
            "stop_reason": context["stop_reason"],
        }

    fast_gates: list[dict[str, Any]] = []
    for cmd in _fast_gate_commands():
        result = runner(cmd, root, None)
        fast_gates.append({"command": cmd, **result})
        if result["returncode"] != 0:
            return {
                "ok": False,
                "iteration": iteration,
                "plan_path": context["plan_path"],
                "fast_gates": fast_gates,
                "business_gate": None,
                "stop_reason": "fast_gate_failed",
            }

    business_cmd = [
        "python3",
        "-m",
        "qa_kb_importer",
    ]
    business_env = {"PYTHONPATH": "src"}
    business_result = runner(business_cmd, root, business_env)
    if business_result["returncode"] != 0:
        return {
            "ok": False,
            "iteration": iteration,
            "plan_path": context["plan_path"],
            "fast_gates": fast_gates,
            "business_gate": business_result,
            "stop_reason": "business_gate_failed",
        }

    return {
        "ok": True,
        "iteration": iteration,
        "plan_path": context["plan_path"],
        "fast_gates": fast_gates,
        "business_gate": business_result,
        "stop_reason": None,
    }


def _load_state(root: Path) -> dict[str, Any]:
    state_path = root / "orchestrator" / "state" / "task-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    validate_state_payload(state)
    return state


def _load_context(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    change = root / state.get("last_outputs", {}).get("change", "")
    review_context = root / state.get("last_outputs", {}).get("review_context", "")
    plan_candidates = _find_iteration_plans(root, int(state["current_iteration"]))
    plan_path = plan_candidates[0] if len(plan_candidates) == 1 else None

    stop_reason = None
    if not change.exists() or not review_context.exists():
        stop_reason = "context_missing"
    elif len(plan_candidates) > 1:
        stop_reason = "plan_conflict"
    elif plan_path is None:
        stop_reason = "plan_missing"

    return {
        "change_path": str(change) if change.exists() else None,
        "review_context_path": str(review_context) if review_context.exists() else None,
        "plan_path": str(plan_path) if plan_path else None,
        "stop_reason": stop_reason,
    }


def _find_iteration_plans(root: Path, iteration: int) -> list[Path]:
    plan_dir = root / "docs" / "exec-plans" / "active"
    if not plan_dir.exists():
        return []
    prefix = f"iter-{iteration:03d}-"
    return [path for path in sorted(plan_dir.glob("*.md")) if path.name.startswith(prefix)]


def _fast_gate_commands() -> list[list[str]]:
    return [
        ["ruff", "format", "--check", "."],
        ["ruff", "check", "."],
        ["python3", "-m", "unittest", "tests/test_orchestrator_v0.py"],
    ]


def _default_command_runner(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict[str, Any]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            env=merged_env,
            check=False,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    except FileNotFoundError as exc:
        return {
            "returncode": 127,
            "stdout": "",
            "stderr": str(exc),
        }
