import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from qa_kb_importer.importer import FixedTemplateImporter, SheetRow
from qa_kb_importer.cli import main


class FixedTemplateImporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.importer = FixedTemplateImporter(
            defect_file=ROOT / "input" / "issue-export-20260408.xlsx",
            testcase_file=ROOT / "input" / "测试用例-scm-20260408.xlsx",
        )

    def test_schema_files_require_display_title(self) -> None:
        defect_schema = yaml.safe_load(
            (ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml").read_text()
        )
        testcase_schema = yaml.safe_load(
            (ROOT / "docs" / "knowledge" / "schemas" / "testcase.schema.yaml").read_text()
        )

        self.assertIn("display_title", defect_schema["schema"]["required"])
        self.assertIn("display_title", defect_schema["schema"]["properties"])
        self.assertIn("display_title", testcase_schema["schema"]["required"])
        self.assertIn("display_title", testcase_schema["schema"]["properties"])

    def test_imports_defect_batch_with_display_title_and_quality_flags(self) -> None:
        defects = self.importer.import_defects(limit=3)

        self.assertEqual(3, len(defects))
        first = defects[0]
        self.assertEqual("defect", first["record_type"])
        self.assertEqual(first["title"], first["display_title"])
        self.assertTrue(first["id"].startswith("DEF-"))
        self.assertIn("source", first)
        self.assertEqual("excel", first["source"]["source_type"])
        self.assertIn("quality_flags", first)
        self.assertIn("steps", first)
        self.assertIsInstance(first["steps"], list)
        self.assertGreater(len(first["steps"]), 0)
        self.assertIn("expected_resolution", first)
        self.assertIn("expected_source_section", first)

    def test_imports_testcase_batch_and_groups_step_rows(self) -> None:
        testcases = self.importer.import_testcases(limit=3)

        self.assertEqual(3, len(testcases))
        first = testcases[0]
        self.assertEqual("testcase", first["record_type"])
        self.assertEqual(first["name"], first["display_title"])
        self.assertTrue(first["id"].startswith("TC-"))
        self.assertEqual(6, len(first["steps"]))
        self.assertIn("零售订单支付成功后，系统自动触发转SO任务", first["steps"][0])
        self.assertIn("SO订单", first["expected"])
        self.assertEqual("excel", first["source"]["source_type"])

    def test_exports_small_batch_into_knowledge_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_root = Path(tmp_dir)
            result = self.importer.export_small_batch(
                knowledge_root=out_root,
                defect_limit=3,
                testcase_limit=3,
            )

            self.assertEqual(3, result["defect_count"])
            self.assertEqual(3, result["testcase_count"])
            self.assertEqual(0, result["error_count"])
            self.assertIn("gate", result)
            self.assertIn("report_path", result)
            self.assertIn("validation_details_path", result)
            self.assertIn("warning_count", result)
            self.assertIn("schema_fail_count", result)
            self.assertIn("quality_warning_count", result)

            expected_dirs = [
                out_root / "imports" / "raw" / "defects",
                out_root / "imports" / "raw" / "testcases",
                out_root / "imports" / "manifests",
                out_root / "imports" / "errors",
                out_root / "imports" / "reports",
                out_root / "snapshots" / "defects",
                out_root / "snapshots" / "testcases",
                out_root / "normalized" / "defects",
                out_root / "normalized" / "testcases",
            ]
            for path in expected_dirs:
                self.assertTrue(path.exists(), path)

            normalized_defects = out_root / "normalized" / "defects"
            normalized_testcases = out_root / "normalized" / "testcases"
            self.assertEqual(3, len(list(normalized_defects.glob("*.yaml"))))
            self.assertEqual(3, len(list(normalized_testcases.glob("*.yaml"))))

            exported = yaml.safe_load(next(normalized_defects.glob("*.yaml")).read_text())
            self.assertEqual(exported["title"], exported["display_title"])

    def test_export_result_includes_gate_summary_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_root = Path(tmp_dir)
            result = self.importer.export_small_batch(
                knowledge_root=out_root,
                defect_limit=2,
                testcase_limit=2,
            )

            self.assertIn("warning_count", result)
            self.assertIn("schema_fail_count", result)
            self.assertIn("quality_warning_count", result)
            self.assertIn("semantic_warning_count", result)
            self.assertIn("warning_rate", result)
            self.assertIn("admissible_warning_count", result)
            self.assertIn("blocking_warning_count", result)

    def test_exports_manifest_with_batch_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_root = Path(tmp_dir)

            result = self.importer.export_small_batch(
                knowledge_root=out_root,
                defect_limit=2,
                testcase_limit=2,
            )

            manifest_files = list((out_root / "imports" / "manifests").glob("*.yaml"))
            self.assertEqual(1, len(manifest_files))

            manifest = yaml.safe_load(manifest_files[0].read_text())
            self.assertEqual(result["import_batch_id"], manifest["import_batch_id"])
            self.assertEqual(2, manifest["defect_count"])
            self.assertEqual(2, manifest["testcase_count"])
            self.assertEqual(0, manifest["error_count"])
            self.assertEqual(self.importer.defect_file.name, manifest["inputs"]["defect_file"])
            self.assertEqual(self.importer.testcase_file.name, manifest["inputs"]["testcase_file"])

    def test_exports_independent_error_list_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_root = Path(tmp_dir)

            result = self.importer.export_small_batch(
                knowledge_root=out_root,
                defect_limit=1,
                testcase_limit=1,
            )

            error_files = list((out_root / "imports" / "errors").glob("*.yaml"))
            self.assertEqual(1, len(error_files))

            error_list = yaml.safe_load(error_files[0].read_text())
            self.assertEqual(result["import_batch_id"], error_list["import_batch_id"])
            self.assertEqual([], error_list["errors"])

    def test_cli_prints_gate_summary_fields(self) -> None:
        summary = {
            "import_batch_id": "batch-test",
            "defect_count": 20,
            "testcase_count": 20,
            "error_count": 0,
            "gate": "warning",
            "warning_count": 6,
            "schema_fail_count": 0,
            "quality_warning_count": 6,
            "semantic_warning_count": 2,
            "admissible_warning_count": 5,
            "blocking_warning_count": 1,
            "warning_rate": 0.15,
            "report_path": "/tmp/report.yaml",
            "validation_details_path": "/tmp/details.yaml",
        }
        with patch("qa_kb_importer.cli.FixedTemplateImporter.export_small_batch", return_value=summary):
            with patch("builtins.print") as print_mock:
                with patch.object(sys, "argv", ["qa_kb_importer"]):
                    exit_code = main()

        self.assertEqual(0, exit_code)
        printed = print_mock.call_args[0][0]
        self.assertIn("gate=warning", printed)
        self.assertIn("warnings=6", printed)
        self.assertIn("semantic_warnings=2", printed)
        self.assertIn("admissible_warnings=5", printed)
        self.assertIn("blocking_warnings=1", printed)
        self.assertIn("warning_rate=0.15", printed)

    def test_normalize_defect_marks_expected_section_present(self) -> None:
        row = SheetRow(
            row_number=5,
            values={
                "ID": "1",
                "标题": "缺陷 A",
                "内容": "### 重现步骤\n步骤1\n### 实际结果\n实际1\n### 期望结果*\n期望1",
                "标签": "area/A",
                "严重程度": "一般",
                "状态": "待处理",
                "来源": "代码开发",
                "环境": "测试",
            },
        )

        defect = self.importer._normalize_defect(row)

        self.assertEqual("expected_section_present", defect["expected_resolution"])
        self.assertEqual("期望结果*", defect["expected_source_section"])

    def test_normalize_defect_marks_expected_missing_but_description_present(self) -> None:
        row = SheetRow(
            row_number=5,
            values={
                "ID": "2",
                "标题": "缺陷 B",
                "内容": "### 缺陷描述*\n这里有现象和预期线索\n### 实际结果\n实际1",
                "标签": "area/A",
                "严重程度": "一般",
                "状态": "待处理",
                "来源": "代码开发",
                "环境": "测试",
            },
        )

        defect = self.importer._normalize_defect(row)

        self.assertEqual("expected_missing_but_description_present", defect["expected_resolution"])
        self.assertEqual("缺陷描述*", defect["expected_source_section"])

    def test_normalize_defect_marks_expected_missing_unrecoverable(self) -> None:
        row = SheetRow(
            row_number=5,
            values={
                "ID": "3",
                "标题": "缺陷 C",
                "内容": "### 重现步骤\n步骤1\n### 实际结果\n实际1",
                "标签": "area/A",
                "严重程度": "一般",
                "状态": "待处理",
                "来源": "代码开发",
                "环境": "测试",
            },
        )

        defect = self.importer._normalize_defect(row)

        self.assertEqual("expected_missing_unrecoverable", defect["expected_resolution"])
        self.assertEqual("", defect["expected_source_section"])


if __name__ == "__main__":
    unittest.main()
