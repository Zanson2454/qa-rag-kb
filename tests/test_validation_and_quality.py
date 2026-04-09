import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from qa_kb_importer.importer import FixedTemplateImporter
from qa_kb_importer.quality import build_batch_quality_report, determine_batch_gate
from qa_kb_importer.validation import validate_normalized_record


class NormalizedValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.importer = FixedTemplateImporter(
            defect_file=ROOT / "input" / "issue-export-20260408.xlsx",
            testcase_file=ROOT / "input" / "测试用例-scm-20260408.xlsx",
        )

    def test_normalized_defect_validation_passes(self) -> None:
        defect = self.importer.import_defects(limit=1)[0]

        result = validate_normalized_record(
            record=defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertTrue(result["passed"])
        self.assertEqual([], result["errors"])

    def test_normalized_testcase_validation_passes(self) -> None:
        testcase = self.importer.import_testcases(limit=1)[0]

        result = validate_normalized_record(
            record=testcase,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "testcase.schema.yaml",
        )

        self.assertTrue(result["passed"])
        self.assertEqual([], result["errors"])

    def test_missing_required_field_fails_validation(self) -> None:
        defect = self.importer.import_defects(limit=1)[0]
        defect.pop("module")

        result = validate_normalized_record(
            record=defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertFalse(result["passed"])
        self.assertIn("missing required field: module", result["errors"])

    def test_missing_display_title_is_identified(self) -> None:
        testcase = self.importer.import_testcases(limit=1)[0]
        testcase["display_title"] = ""

        result = validate_normalized_record(
            record=testcase,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "testcase.schema.yaml",
        )

        self.assertFalse(result["passed"])
        self.assertGreater(result["metrics"]["missing_display_title_count"], 0)

    def test_warning_details_are_structured(self) -> None:
        defect = self.importer.import_defects(limit=1)[0]
        defect["expected"] = ""
        defect["expected_resolution"] = "expected_missing_but_description_present"
        defect["expected_source_section"] = "缺陷描述*"

        result = validate_normalized_record(
            record=defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        detail = result["warning_details"][0]
        self.assertEqual("missing_expected", detail["code"])
        self.assertEqual("warning", detail["severity"])
        self.assertIn("expected", detail["message"])
        self.assertIn("补充", detail["suggestion"])
        self.assertEqual("expected", detail["source_field"])
        self.assertEqual("缺陷描述*", detail["source_section"])
        self.assertEqual("admissible", detail["admission"])

    def test_defect_semantic_warnings_are_reported_with_codes(self) -> None:
        defect = self.importer.import_defects(limit=1)[0]
        defect["steps"] = []
        defect["expected"] = ""
        defect["actual"] = ""

        result = validate_normalized_record(
            record=defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertIn("missing_steps", result["warning_codes"])
        self.assertIn("missing_expected", result["warning_codes"])
        self.assertIn("missing_actual", result["warning_codes"])

    def test_missing_expected_can_be_blocking_when_unrecoverable(self) -> None:
        defect = self.importer.import_defects(limit=1)[0]
        defect["expected"] = ""
        defect["expected_resolution"] = "expected_missing_unrecoverable"
        defect["expected_source_section"] = ""

        result = validate_normalized_record(
            record=defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        missing_expected_detail = next(
            detail for detail in result["warning_details"] if detail["code"] == "missing_expected"
        )
        self.assertEqual("blocking", missing_expected_detail["admission"])

    def test_testcase_semantic_warnings_are_reported_with_codes(self) -> None:
        testcase = self.importer.import_testcases(limit=1)[0]
        testcase["steps"] = []
        testcase["expected"] = ""

        result = validate_normalized_record(
            record=testcase,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "testcase.schema.yaml",
        )

        self.assertIn("testcase_steps_missing", result["warning_codes"])
        self.assertIn("testcase_expected_missing", result["warning_codes"])


class BatchQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.importer = FixedTemplateImporter(
            defect_file=ROOT / "input" / "issue-export-20260408.xlsx",
            testcase_file=ROOT / "input" / "测试用例-scm-20260408.xlsx",
        )

    def test_batch_quality_report_is_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_root = Path(tmp_dir)
            export_result = self.importer.export_small_batch(
                knowledge_root=out_root,
                defect_limit=2,
                testcase_limit=2,
            )

            report_files = list((out_root / "imports" / "reports").glob("*-report.yaml"))
            detail_files = list((out_root / "imports" / "reports").glob("*-validation-details.yaml"))

            self.assertEqual(1, len(report_files))
            self.assertEqual(1, len(detail_files))

            report = yaml.safe_load(report_files[0].read_text())
            self.assertEqual(export_result["import_batch_id"], report["batch_id"])
            self.assertEqual("excel", report["source_type"])
            self.assertIn(report["gate"], {"passed", "warning", "failed"})
            self.assertEqual(str(detail_files[0]), report["details_file"])

    def test_batch_gate_can_return_passed(self) -> None:
        gate = determine_batch_gate(
            schema_fail_count=0,
            error_count=0,
            admissible_warning_count=0,
            blocking_warning_count=0,
            record_count=20,
        )
        self.assertEqual("passed", gate)

    def test_batch_gate_can_return_warning(self) -> None:
        gate = determine_batch_gate(
            schema_fail_count=0,
            error_count=0,
            admissible_warning_count=3,
            blocking_warning_count=1,
            record_count=20,
        )
        self.assertEqual("warning", gate)

    def test_batch_gate_can_return_failed(self) -> None:
        gate = determine_batch_gate(
            schema_fail_count=1,
            error_count=0,
            admissible_warning_count=0,
            blocking_warning_count=0,
            record_count=20,
        )
        self.assertEqual("failed", gate)

    def test_batch_gate_fails_when_error_records_exist(self) -> None:
        gate = determine_batch_gate(
            schema_fail_count=0,
            error_count=1,
            admissible_warning_count=0,
            blocking_warning_count=0,
            record_count=20,
        )
        self.assertEqual("failed", gate)

    def test_batch_gate_fails_when_blocking_warning_rate_exceeds_threshold(self) -> None:
        gate = determine_batch_gate(
            schema_fail_count=0,
            error_count=0,
            admissible_warning_count=8,
            blocking_warning_count=7,
            record_count=20,
        )
        self.assertEqual("failed", gate)

    def test_quality_report_distinguishes_schema_fail_and_quality_warning(self) -> None:
        validations = [
            {
                "passed": True,
                "errors": [],
                "warnings": ["missing_expected"],
                "warning_codes": ["missing_expected"],
                "warning_details": [
                    {
                        "code": "missing_expected",
                        "severity": "warning",
                        "message": "expected is empty",
                        "suggestion": "补充 expected 字段",
                        "category": "semantic",
                        "source_field": "expected",
                        "source_section": "缺陷描述*",
                        "admission": "admissible",
                    }
                ],
                "metrics": {
                    "missing_required_field_count": 0,
                    "missing_display_title_count": 0,
                    "missing_core_field_count": 1,
                },
                "quality_flags": ["missing_expected_section"],
            },
            {
                "passed": False,
                "errors": ["missing required field: module"],
                "warnings": [],
                "warning_codes": [],
                "warning_details": [],
                "metrics": {
                    "missing_required_field_count": 1,
                    "missing_display_title_count": 0,
                    "missing_core_field_count": 0,
                },
                "quality_flags": [],
            },
        ]

        report = build_batch_quality_report(
            batch_id="batch-test",
            source_type="excel",
            manifest={"defect_count": 1, "testcase_count": 1},
            error_list={"errors": []},
            validation_results=validations,
            details_file="details.yaml",
            testcase_step_row_count_before_grouping=4,
            testcase_case_count_after_grouping=2,
        )

        self.assertEqual(1, report["schema_fail_count"])
        self.assertEqual(1, report["quality_warning_count"])
        self.assertEqual(1, report["semantic_warning_count"])
        self.assertEqual(1, report["admissible_warning_count"])
        self.assertEqual(0, report["blocking_warning_count"])
        self.assertEqual(1, report["missing_required_field_count"])
        self.assertEqual(1, report["missing_core_field_count"])
        self.assertEqual("warning", report["quality_status"])
        self.assertEqual({"missing_expected": 1}, report["warning_code_distribution"])
        self.assertEqual({"warning": 1}, report["warning_severity_distribution"])
        self.assertEqual({"admissible": 1}, report["admission_distribution"])


if __name__ == "__main__":
    unittest.main()
