from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestrator.artifacts import find_latest_artifacts, read_evaluation_summary
from orchestrator.prompting import render_prompt
from orchestrator.run_loop import run_local_loop
from orchestrator.state_machine import decide_next
from orchestrator.validation import validate_state_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orchestrator v0")
    parser.add_argument("command", choices=["next", "loop"])
    parser.add_argument("--root", default=".", help="项目根目录")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    try:
        if args.command == "next":
            run_next(root)
            return 0
        if args.command == "loop":
            run_loop(root)
            return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 1


def run_next(root: Path) -> None:
    state_path = root / "orchestrator" / "state" / "task-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    validate_state_payload(state)
    artifacts = find_latest_artifacts(root)
    evaluation_summary = read_evaluation_summary(artifacts.evaluation)
    decision = decide_next(state, artifacts, evaluation_summary)
    _, prompt_path = render_prompt(root, state, artifacts, decision)

    state["decision"] = {
        "next_action": decision.next_action,
        "reason": decision.reason,
        "prompt_file": str(prompt_path.relative_to(root)),
    }
    state["last_outputs"] = {
        "change": _relative_or_missing(root, artifacts.change),
        "evaluation": _relative_or_missing(root, artifacts.evaluation),
        "reflection": _relative_or_missing(root, artifacts.reflection),
        "review_context": _relative_or_missing(root, artifacts.review_context),
    }
    state["last_evaluation"] = evaluation_summary
    state["current_state"] = decision.next_state
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    history = list(state.get("history", []))
    history.append(
        {
            "state": decision.next_state,
            "action": decision.next_action,
            "reason": decision.reason,
        }
    )
    state["history"] = history[-10:]
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def run_loop(root: Path) -> None:
    state_path = root / "orchestrator" / "state" / "task-state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    validate_state_payload(state)

    result = run_local_loop(root)
    state["last_loop"] = {
        "ok": result["ok"],
        "iteration": result["iteration"],
        "plan_path": result["plan_path"],
        "stop_reason": result["stop_reason"],
        "human_gate": True,
    }
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"loop iteration={result['iteration']} ok={str(result['ok']).lower()} "
        f"stop_reason={result['stop_reason'] or 'none'}"
    )


def _relative_or_missing(root: Path, path: Path | None) -> str:
    if path is None:
        return "missing"
    return str(path.relative_to(root))


if __name__ == "__main__":
    raise SystemExit(main())
