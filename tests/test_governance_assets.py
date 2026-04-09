import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GovernanceAssetsTests(unittest.TestCase):
    def test_agents_md_includes_mainline_governance_rules(self) -> None:
        content = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("同一 iteration 不允许并行推进两个不同主题的主线", content)
        self.assertIn("`task-state.json` 是当前确认主线的唯一状态源", content)
        self.assertIn("必须显式对照对应 plan 的 `done_criteria`", content)
        self.assertIn("governance/documentation 主线与 implementation 主线不得共用 iteration 编号", content)

    def test_project_skills_exist(self) -> None:
        self.assertTrue((ROOT / "skills" / "iteration-start-review" / "SKILL.md").exists())
        self.assertTrue((ROOT / "skills" / "acceptance-closure" / "SKILL.md").exists())

    def test_project_skill_metadata_is_complete(self) -> None:
        required_sections = [
            "goal",
            "trigger_conditions",
            "inputs",
            "outputs",
            "acceptance_criteria",
            "out_of_scope",
            "owner",
            "dependencies",
        ]
        for path in [
            ROOT / "skills" / "iteration-start-review" / "SKILL.md",
            ROOT / "skills" / "acceptance-closure" / "SKILL.md",
        ]:
            content = path.read_text(encoding="utf-8")
            self.assertIn("name:", content)
            self.assertIn("description:", content)
            for section in required_sections:
                self.assertIn(f"## {section}", content)


if __name__ == "__main__":
    unittest.main()
