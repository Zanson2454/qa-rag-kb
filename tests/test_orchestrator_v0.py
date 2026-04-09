import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class OrchestratorV0Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self._create_layout()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _create_layout(self) -> None:
        for rel in [
            "harness/changes",
            "harness/evaluations",
            "harness/reflections",
            "harness/review-contexts",
            "orchestrator/prompts",
            "orchestrator/state",
            "orchestrator/runs",
            "docs/whitepaper",
        ]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)

        (self.root / "orchestrator" / "prompts" / "implement.md").write_text(
            "impl {{task_id}} {{current_goal}} {{decision_reason}}\n"
        )
        (self.root / "orchestrator" / "prompts" / "reflect.md").write_text(
            "reflect {{task_id}} {{current_goal}} {{decision_reason}}\n"
        )
        (self.root / "orchestrator" / "prompts" / "continue.md").write_text(
            "continue {{task_id}} {{current_goal}} {{decision_reason}}\n"
        )
        (self.root / "orchestrator" / "prompts" / "plan.md").write_text(
            "plan {{task_id}} {{current_goal}} {{decision_reason}}\n"
        )
        (self.root / "orchestrator" / "prompts" / "evaluate.md").write_text(
            "evaluate {{task_id}} {{current_goal}} {{decision_reason}}\n"
        )

        (self.root / "harness" / "changes" / "iter-005-change.md").write_text(
            "# change\n"
        )
        (self.root / "harness" / "evaluations" / "iter-005-eval.md").write_text(
            "evaluation:\n  passed: true\n"
        )
        (self.root / "harness" / "reflections" / "iter-005-reflection.md").write_text(
            "# reflection\n"
        )
        (self.root / "harness" / "review-contexts" / "iter-006-context.md").write_text(
            "# context\n"
        )

    def _write_state(self, payload: dict) -> None:
        (self.root / "orchestrator" / "state" / "task-state.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _run_next(self) -> subprocess.CompletedProcess[str]:
        env = dict(**{"PYTHONPATH": str(ROOT)})
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "orchestrator" / "run.py"),
                "next",
                "--root",
                str(self.root),
            ],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def test_passed_evaluation_moves_to_evaluating_and_generates_implement_prompt(
        self,
    ) -> None:
        self._write_state(
            {
                "task_id": "task-1",
                "current_iteration": 5,
                "current_state": "implementing",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertEqual(0, result.returncode)

        state = json.loads(
            (self.root / "orchestrator" / "state" / "task-state.json").read_text()
        )
        self.assertEqual("evaluating", state["current_state"])
        self.assertEqual("implement", state["decision"]["next_action"])
        generated = list((self.root / "orchestrator" / "runs").glob("*.md"))
        self.assertEqual(1, len(generated))
        self.assertIn("impl task-1", generated[0].read_text())

    def test_missing_key_artifacts_enters_blocked(self) -> None:
        (self.root / "harness" / "evaluations" / "iter-005-eval.md").unlink()
        self._write_state(
            {
                "task_id": "task-2",
                "current_iteration": 5,
                "current_state": "planning",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertEqual(0, result.returncode)

        state = json.loads(
            (self.root / "orchestrator" / "state" / "task-state.json").read_text()
        )
        self.assertEqual("blocked", state["current_state"])
        self.assertEqual("continue", state["decision"]["next_action"])

    def test_exceeding_retry_limit_enters_failed(self) -> None:
        (self.root / "harness" / "evaluations" / "iter-005-eval.md").write_text(
            "evaluation:\n  passed: false\n"
        )
        self._write_state(
            {
                "task_id": "task-3",
                "current_iteration": 5,
                "current_state": "reflecting",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 3},
            }
        )

        result = self._run_next()
        self.assertEqual(0, result.returncode)

        state = json.loads(
            (self.root / "orchestrator" / "state" / "task-state.json").read_text()
        )
        self.assertEqual("failed", state["current_state"])
        self.assertEqual("continue", state["decision"]["next_action"])

    def test_created_state_moves_to_planning_with_plan_prompt(self) -> None:
        self._write_state(
            {
                "task_id": "task-4",
                "current_iteration": 1,
                "current_state": "created",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertEqual(0, result.returncode)

        state = json.loads(
            (self.root / "orchestrator" / "state" / "task-state.json").read_text()
        )
        self.assertEqual("planning", state["current_state"])
        self.assertEqual("plan", state["decision"]["next_action"])
        generated = list((self.root / "orchestrator" / "runs").glob("*.md"))
        self.assertEqual(1, len(generated))
        self.assertIn("plan task-4", generated[0].read_text())

    def test_evaluating_state_moves_to_completed_when_evaluation_passed(self) -> None:
        self._write_state(
            {
                "task_id": "task-5",
                "current_iteration": 5,
                "current_state": "evaluating",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertEqual(0, result.returncode)

        state = json.loads(
            (self.root / "orchestrator" / "state" / "task-state.json").read_text()
        )
        self.assertEqual("completed", state["current_state"])
        self.assertEqual("continue", state["decision"]["next_action"])

    def test_invalid_state_file_returns_error(self) -> None:
        self._write_state(
            {
                "task_id": "task-6",
                "current_iteration": 5,
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("current_state", result.stderr)

    def test_invalid_current_plan_shape_returns_error(self) -> None:
        self._write_state(
            {
                "task_id": "task-6b",
                "current_iteration": 5,
                "current_state": "evaluating",
                "current_goal": "goal",
                "current_plan": {
                    "iteration": "5",
                    "path": "docs/exec-plans/active/iter-005-plan.md",
                },
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("current_plan.iteration", result.stderr)

    def test_unreplaced_placeholder_in_prompt_causes_error(self) -> None:
        (self.root / "orchestrator" / "prompts" / "continue.md").write_text(
            "continue {{task_id}} {{unknown_placeholder}}\n"
        )
        self._write_state(
            {
                "task_id": "task-7",
                "current_iteration": 5,
                "current_state": "blocked",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("placeholder", result.stderr)

    def test_passed_evaluation_with_errors_enters_reflecting(self) -> None:
        (self.root / "harness" / "evaluations" / "iter-005-eval.md").write_text(
            "evaluation:\n  passed: true\n  score: 88\n  errors:\n    - schema mismatch\n  suggestions:\n    - fix schema\n",
            encoding="utf-8",
        )
        self._write_state(
            {
                "task_id": "task-8",
                "current_iteration": 5,
                "current_state": "planning",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertEqual(0, result.returncode)

        state = json.loads(
            (self.root / "orchestrator" / "state" / "task-state.json").read_text()
        )
        self.assertEqual("reflecting", state["current_state"])
        self.assertEqual("reflect", state["decision"]["next_action"])
        self.assertIn("errors", state["decision"]["reason"])

    def test_state_records_evaluation_summary_fields(self) -> None:
        (self.root / "harness" / "evaluations" / "iter-005-eval.md").write_text(
            "evaluation:\n  passed: true\n  score: 95\n  errors: []\n  suggestions:\n    - add coverage\n",
            encoding="utf-8",
        )
        self._write_state(
            {
                "task_id": "task-9",
                "current_iteration": 5,
                "current_state": "evaluating",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertEqual(0, result.returncode)

        state = json.loads(
            (self.root / "orchestrator" / "state" / "task-state.json").read_text()
        )
        self.assertEqual(True, state["last_evaluation"]["passed"])
        self.assertEqual(95, state["last_evaluation"]["score"])
        self.assertEqual([], state["last_evaluation"]["errors"])
        self.assertEqual(["add coverage"], state["last_evaluation"]["suggestions"])

    def test_markdown_evaluation_summary_is_extracted_from_realistic_format(
        self,
    ) -> None:
        (self.root / "harness" / "evaluations" / "iter-005-eval.md").write_text(
            "# Eval\n\n"
            "evaluation:\n"
            "  passed: true\n"
            "  score: 91\n"
            "  errors: []\n"
            "  suggestions:\n"
            "    - add coverage\n"
            "    - tighten checks\n\n"
            "## Notes\n\ntext\n",
            encoding="utf-8",
        )
        self._write_state(
            {
                "task_id": "task-10",
                "current_iteration": 5,
                "current_state": "evaluating",
                "current_goal": "goal",
                "last_outputs": {},
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

        result = self._run_next()
        self.assertEqual(0, result.returncode)

        state = json.loads(
            (self.root / "orchestrator" / "state" / "task-state.json").read_text()
        )
        self.assertEqual(True, state["last_evaluation"]["passed"])
        self.assertEqual(91, state["last_evaluation"]["score"])
        self.assertEqual([], state["last_evaluation"]["errors"])
        self.assertEqual(
            ["add coverage", "tighten checks"], state["last_evaluation"]["suggestions"]
        )


class RepositoryStateFileTests(unittest.TestCase):
    def test_repository_state_file_tracks_existing_iteration_outputs(self) -> None:
        state = json.loads(
            (ROOT / "orchestrator" / "state" / "task-state.json").read_text()
        )

        current_iteration = state["current_iteration"]
        self.assertIsInstance(current_iteration, int)

        expected_pairs = {
            "change": current_iteration,
            "evaluation": current_iteration,
            "reflection": current_iteration,
            "review_context": current_iteration + 1,
        }
        for key, expected_iter in expected_pairs.items():
            rel_path = state["last_outputs"][key]
            self.assertTrue((ROOT / rel_path).exists(), rel_path)
            match = re.search(r"iter-(\d+)-", Path(rel_path).name)
            self.assertIsNotNone(match, rel_path)
            self.assertEqual(expected_iter, int(match.group(1)), rel_path)

    def test_repository_state_file_current_plan_matches_iteration(self) -> None:
        state = json.loads(
            (ROOT / "orchestrator" / "state" / "task-state.json").read_text()
        )

        current_plan = state["current_plan"]
        self.assertEqual(state["current_iteration"], current_plan["iteration"])
        self.assertTrue((ROOT / current_plan["path"]).exists(), current_plan["path"])


if __name__ == "__main__":
    unittest.main()
