import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LoopRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self._create_layout()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _create_layout(self) -> None:
        for rel in [
            "docs/exec-plans/active",
            "harness/changes",
            "harness/review-contexts",
            "orchestrator/state",
            "tests",
        ]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)

        (self.root / "AGENTS.md").write_text("# rules\n", encoding="utf-8")
        (self.root / "harness" / "changes" / "iter-012-change.md").write_text("# change\n", encoding="utf-8")
        (self.root / "harness" / "review-contexts" / "iter-013-context.md").write_text("# context\n", encoding="utf-8")
        (self.root / "docs" / "exec-plans" / "active" / "iter-013-sample-plan.md").write_text(
            "# plan\n",
            encoding="utf-8",
        )
        (self.root / "tests" / "test_orchestrator_v0.py").write_text("import unittest\n", encoding="utf-8")
        self._write_state(
            {
                "task_id": "qa-rag-kb-main",
                "current_iteration": 13,
                "current_state": "implementing",
                "current_goal": "goal",
                "current_plan": {
                    "iteration": 13,
                    "path": "docs/exec-plans/active/iter-013-sample-plan.md",
                },
                "last_outputs": {
                    "change": "harness/changes/iter-012-change.md",
                    "review_context": "harness/review-contexts/iter-013-context.md",
                },
                "decision": {},
                "limits": {"max_retry": 3, "retry_count": 0},
            }
        )

    def _write_state(self, payload: dict) -> None:
        (self.root / "orchestrator" / "state" / "task-state.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def test_loads_required_context_and_plan(self) -> None:
        from orchestrator.run_loop import run_local_loop

        result = run_local_loop(self.root, command_runner=self._successful_command_runner)

        self.assertTrue(result["ok"])
        self.assertEqual(13, result["iteration"])
        self.assertTrue(result["plan_path"].endswith("iter-013-sample-plan.md"))

    def test_blocks_when_plan_missing(self) -> None:
        from orchestrator.run_loop import run_local_loop

        (self.root / "docs" / "exec-plans" / "active" / "iter-013-sample-plan.md").unlink()
        result = run_local_loop(self.root, command_runner=self._successful_command_runner)

        self.assertFalse(result["ok"])
        self.assertEqual("plan_missing", result["stop_reason"])

    def test_blocks_when_multiple_iteration_plans_exist(self) -> None:
        from orchestrator.run_loop import run_local_loop

        (self.root / "docs" / "exec-plans" / "active" / "iter-013-other-plan.md").write_text(
            "# other plan\n",
            encoding="utf-8",
        )
        result = run_local_loop(self.root, command_runner=self._successful_command_runner)

        self.assertTrue(result["ok"])
        self.assertTrue(result["plan_path"].endswith("iter-013-sample-plan.md"))

    def test_blocks_when_current_plan_file_missing(self) -> None:
        from orchestrator.run_loop import run_local_loop

        (self.root / "docs" / "exec-plans" / "active" / "iter-013-sample-plan.md").unlink()
        result = run_local_loop(self.root, command_runner=self._successful_command_runner)

        self.assertFalse(result["ok"])
        self.assertEqual("plan_missing", result["stop_reason"])

    def test_blocks_when_current_plan_iteration_mismatches(self) -> None:
        from orchestrator.run_loop import run_local_loop

        state_path = self.root / "orchestrator" / "state" / "task-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["current_plan"]["iteration"] = 12
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

        result = run_local_loop(self.root, command_runner=self._successful_command_runner)

        self.assertFalse(result["ok"])
        self.assertEqual("plan_iteration_mismatch", result["stop_reason"])

    def test_runs_fast_gates_before_business_gate(self) -> None:
        from orchestrator.run_loop import run_local_loop

        calls: list[list[str]] = []

        def runner(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict:
            calls.append(cmd)
            return {"returncode": 0, "stdout": "ok", "stderr": ""}

        result = run_local_loop(self.root, command_runner=runner)

        self.assertTrue(result["ok"])
        self.assertEqual(["ruff", "format", "--check", "."], calls[0])
        self.assertEqual(["ruff", "check", "."], calls[1])
        self.assertEqual(["python3", "-m", "unittest", "tests/test_orchestrator_v0.py"], calls[2])
        self.assertEqual(["python3", "-m", "qa_kb_importer"], calls[3][:3])

    def test_stops_when_fast_gate_fails(self) -> None:
        from orchestrator.run_loop import run_local_loop

        calls: list[list[str]] = []

        def runner(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict:
            calls.append(cmd)
            if cmd[:2] == ["ruff", "check"]:
                return {"returncode": 1, "stdout": "", "stderr": "lint error"}
            return {"returncode": 0, "stdout": "ok", "stderr": ""}

        result = run_local_loop(self.root, command_runner=runner)

        self.assertFalse(result["ok"])
        self.assertEqual("fast_gate_failed", result["stop_reason"])
        self.assertEqual(2, len(calls))

    def test_stops_when_business_gate_fails(self) -> None:
        from orchestrator.run_loop import run_local_loop

        def runner(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> dict:
            if cmd[:3] == ["python3", "-m", "qa_kb_importer"]:
                return {"returncode": 1, "stdout": "gate=failed", "stderr": "batch failed"}
            return {"returncode": 0, "stdout": "ok", "stderr": ""}

        result = run_local_loop(self.root, command_runner=runner)

        self.assertFalse(result["ok"])
        self.assertEqual("business_gate_failed", result["stop_reason"])
        self.assertEqual("gate=failed", result["business_gate"]["stdout"])

    def test_run_cli_loop_updates_state_with_summary(self) -> None:
        env = {"PYTHONPATH": str(ROOT)}
        result = subprocess.run(
            [sys.executable, str(ROOT / "orchestrator" / "run.py"), "loop", "--root", str(self.root)],
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        state = json.loads((self.root / "orchestrator" / "state" / "task-state.json").read_text(encoding="utf-8"))
        self.assertIn("last_loop", state)
        self.assertIn("human_gate", state["last_loop"])
        self.assertIn("stop_reason", state["last_loop"])
        self.assertIn("plan_path", state["last_loop"])
        self.assertIn("loop", result.stdout)

    def _successful_command_runner(
        self,
        cmd: list[str],
        cwd: Path,
        env: dict[str, str] | None = None,
    ) -> dict:
        return {"returncode": 0, "stdout": "ok", "stderr": ""}


if __name__ == "__main__":
    unittest.main()
