import importlib
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load_validation_symbols() -> tuple[object, object, object, object]:
    importer_module = importlib.import_module("qa_kb_importer.importer")
    quality_module = importlib.import_module("qa_kb_importer.quality")
    validation_module = importlib.import_module("qa_kb_importer.validation")
    return (
        importer_module.FixedTemplateImporter,
        importer_module.SheetRow,
        quality_module.build_batch_quality_report,
        quality_module.determine_batch_gate,
        validation_module.validate_normalized_record,
    )


(
    FixedTemplateImporter,
    SheetRow,
    build_batch_quality_report,
    determine_batch_gate,
    validate_normalized_record,
) = _load_validation_symbols()


class SymptomOnlyDefectImporter(FixedTemplateImporter):
    def __init__(self, defect_rows: list[SheetRow]) -> None:
        super().__init__(
            defect_file=ROOT / "input" / "issue-export-20260408.xlsx",
            testcase_file=ROOT / "input" / "测试用例-scm-20260408.xlsx",
        )
        self._defect_rows = defect_rows

    def _read_defect_rows(self):
        return self._defect_rows

    def _read_testcase_cases(self):
        return []


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
            schema_path=ROOT
            / "docs"
            / "knowledge"
            / "schemas"
            / "testcase.schema.yaml",
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
            schema_path=ROOT
            / "docs"
            / "knowledge"
            / "schemas"
            / "testcase.schema.yaml",
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
        defect = {
            "id": "DEF-SEM-1",
            "record_type": "defect",
            "title": "普通缺陷记录",
            "display_title": "普通缺陷记录",
            "module": "area/A",
            "severity": "一般",
            "steps": [],
            "expected": "",
            "actual": "",
            "content_text": "这是普通缺陷记录，不包含确认型问题语义。",
            "quality_flags": [],
        }

        result = validate_normalized_record(
            record=defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertIn("missing_steps", result["warning_codes"])
        self.assertIn("missing_expected", result["warning_codes"])
        self.assertIn("missing_actual", result["warning_codes"])

    def test_recovered_expected_candidate_suppresses_missing_expected_warning(
        self,
    ) -> None:
        defect = self.importer._normalize_defect(
            SheetRow(
                row_number=5,
                values={
                    "ID": "4",
                    "标题": "导入失败缺陷",
                    "内容": "### 缺陷描述*\n导入失败，任务执行失败后无法继续\n### 重现步骤\n步骤1\n步骤2\n### 实际结果\n导入失败",
                    "标签": "area/A",
                    "严重程度": "一般",
                    "状态": "待处理",
                    "来源": "代码开发",
                    "环境": "测试",
                },
            )
        )

        result = validate_normalized_record(
            record=defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertNotIn("missing_expected", result["warning_codes"])
        self.assertIn("generated_expected_candidate", result["quality_flags"])

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
            detail
            for detail in result["warning_details"]
            if detail["code"] == "missing_expected"
        )
        self.assertEqual("blocking", missing_expected_detail["admission"])

    def test_question_like_defect_emits_dedicated_warning_code(self) -> None:
        record = {
            "id": "DEF-Q-1",
            "record_type": "defect",
            "title": "这个场景需要确认吗？",
            "display_title": "这个场景需要确认吗？",
            "module": "area/A",
            "severity": "一般",
            "steps": ["请确认是否继续处理"],
            "expected": "",
            "actual": "",
            "content_text": "这是一个确认型问题，请确认当前处理方式。",
            "quality_flags": ["missing_expected_section"],
        }

        result = validate_normalized_record(
            record=record,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertIn("question_like_record", result["warning_codes"])
        question_detail = next(
            detail
            for detail in result["warning_details"]
            if detail["code"] == "question_like_record"
        )
        self.assertEqual("blocking", question_detail["admission"])
        self.assertNotEqual("missing_expected", question_detail["code"])

    def test_question_like_defect_does_not_trigger_from_steps_only(self) -> None:
        record = {
            "id": "DEF-Q-STEP",
            "record_type": "defect",
            "title": "普通缺陷记录",
            "display_title": "普通缺陷记录",
            "module": "area/A",
            "severity": "一般",
            "steps": ["请确认是否继续处理"],
            "expected": "",
            "actual": "",
            "content_text": "这是普通缺陷记录，不包含确认型问题语义。",
            "quality_flags": ["missing_expected_section"],
        }

        result = validate_normalized_record(
            record=record,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertNotIn("question_like_record", result["warning_codes"])
        self.assertIn("missing_expected", result["warning_codes"])

    def test_bundle_like_defect_is_admissible_without_auto_expected(self) -> None:
        row = SheetRow(
            row_number=9,
            values={
                "ID": "9",
                "标题": "问题若干：布局调整，需要产品确认",
                "内容": (
                    "### 缺陷描述*\n"
                    "问题若干，涉及布局调整与需要产品确认的事项。\n"
                    "### 重现步骤\n"
                    "步骤1\n步骤2\n"
                    "### 实际结果\n"
                    "当前表现待确认"
                ),
                "标签": "area/A",
                "严重程度": "一般",
                "状态": "待处理",
                "来源": "代码开发",
                "环境": "测试",
            },
        )

        defect = self.importer._normalize_defect(row)

        self.assertEqual("", defect["expected"])
        self.assertNotIn("generated_expected_candidate", defect["quality_flags"])

        result = validate_normalized_record(
            record=defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertIn("bundle_like_record", result["warning_codes"])
        bundle_detail = next(
            detail
            for detail in result["warning_details"]
            if detail["code"] == "bundle_like_record"
        )
        self.assertEqual("admissible", bundle_detail["admission"])

    def test_bundle_like_defect_does_not_trigger_from_steps_only(self) -> None:
        record = {
            "id": "DEF-B-STEP",
            "record_type": "defect",
            "title": "普通缺陷记录",
            "display_title": "普通缺陷记录",
            "module": "area/A",
            "severity": "一般",
            "steps": ["需要产品确认后再继续处理"],
            "expected": "",
            "actual": "当前表现待确认",
            "content_text": "这是普通缺陷记录，不包含 bundle 型标题或正文。",
            "quality_flags": ["missing_expected_section"],
        }

        result = validate_normalized_record(
            record=record,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertNotIn("bundle_like_record", result["warning_codes"])
        self.assertIn("missing_expected", result["warning_codes"])

    def test_testcase_semantic_warnings_are_reported_with_codes(self) -> None:
        testcase = self.importer.import_testcases(limit=1)[0]
        testcase["steps"] = []
        testcase["expected"] = ""

        result = validate_normalized_record(
            record=testcase,
            schema_path=ROOT
            / "docs"
            / "knowledge"
            / "schemas"
            / "testcase.schema.yaml",
        )

        self.assertIn("testcase_steps_missing", result["warning_codes"])
        self.assertIn("testcase_expected_missing", result["warning_codes"])

    def test_special_record_types_are_split_from_generic_missing_expected(self) -> None:
        recovered_defect = self.importer._normalize_defect(
            SheetRow(
                row_number=11,
                values={
                    "ID": "11",
                    "标题": "没保存上",
                    "内容": (
                        "### 缺陷描述*\n"
                        "页面表现待确认，标题已经说明问题场景。\n"
                        "### 重现步骤\n"
                        "步骤1\n步骤2\n"
                        "### 实际结果\n"
                        "当前表现待确认"
                    ),
                    "标签": "area/A",
                    "严重程度": "一般",
                    "状态": "待处理",
                    "来源": "代码开发",
                    "环境": "测试",
                },
            )
        )
        question_like_record = {
            "id": "DEF-Q-2",
            "record_type": "defect",
            "title": "这个处理方式需要确认吗？",
            "display_title": "这个处理方式需要确认吗？",
            "module": "area/A",
            "severity": "一般",
            "steps": ["请确认是否继续处理"],
            "expected": "",
            "actual": "",
            "content_text": "这是一个确认型问题，请确认当前处理方式。",
            "quality_flags": ["missing_expected_section"],
        }

        bundle_like_defect = self.importer._normalize_defect(
            SheetRow(
                row_number=12,
                values={
                    "ID": "12",
                    "标题": "问题集合：布局调整，需要产品确认",
                    "内容": (
                        "### 缺陷描述*\n"
                        "问题集合，涉及布局调整与需要产品确认的事项。\n"
                        "### 重现步骤\n"
                        "步骤1\n步骤2\n"
                        "### 实际结果\n"
                        "当前表现待确认"
                    ),
                    "标签": "area/A",
                    "严重程度": "一般",
                    "状态": "待处理",
                    "来源": "代码开发",
                    "环境": "测试",
                },
            )
        )

        recovered_result = validate_normalized_record(
            record=recovered_defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )
        question_result = validate_normalized_record(
            record=question_like_record,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )
        bundle_result = validate_normalized_record(
            record=bundle_like_defect,
            schema_path=ROOT / "docs" / "knowledge" / "schemas" / "defect.schema.yaml",
        )

        self.assertNotIn("missing_expected", recovered_result["warning_codes"])
        self.assertIn("question_like_record", question_result["warning_codes"])
        self.assertIn("bundle_like_record", bundle_result["warning_codes"])

        report = build_batch_quality_report(
            batch_id="batch-test",
            source_type="excel",
            manifest={"defect_count": 3, "testcase_count": 0},
            error_list={"errors": []},
            validation_results=[
                recovered_result,
                question_result,
                bundle_result,
            ],
            details_file="details.yaml",
            testcase_step_row_count_before_grouping=0,
            testcase_case_count_after_grouping=0,
        )

        self.assertNotIn("missing_expected", report["warning_code_distribution"])
        self.assertEqual(1, report["warning_code_distribution"]["question_like_record"])
        self.assertEqual(1, report["warning_code_distribution"]["bundle_like_record"])


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

            report_files = list(
                (out_root / "imports" / "reports").glob("*-report.yaml")
            )
            detail_files = list(
                (out_root / "imports" / "reports").glob("*-validation-details.yaml")
            )

            self.assertEqual(1, len(report_files))
            self.assertEqual(1, len(detail_files))

            report = yaml.safe_load(report_files[0].read_text())
            self.assertEqual(export_result["import_batch_id"], report["batch_id"])
            self.assertEqual("excel", report["source_type"])
            self.assertIn(report["gate"], {"passed", "warning", "failed"})
            self.assertEqual(str(detail_files[0]), report["details_file"])

    def test_batch_quality_report_drops_missing_expected_after_recovery(
        self,
    ) -> None:
        baseline_validations = [
            validate_normalized_record(
                record={
                    "id": "DEF-41",
                    "record_type": "defect",
                    "title": "导入失败缺陷",
                    "display_title": "导入失败缺陷",
                    "module": "area/A",
                    "severity": "一般",
                    "steps": ["步骤1", "步骤2"],
                    "expected": "",
                    "expected_resolution": "expected_missing_but_description_present",
                    "expected_source_section": "缺陷描述*",
                    "actual": "导入失败",
                    "content_text": "导入失败缺陷",
                    "quality_flags": ["missing_expected_section"],
                },
                schema_path=ROOT
                / "docs"
                / "knowledge"
                / "schemas"
                / "defect.schema.yaml",
            ),
            validate_normalized_record(
                record={
                    "id": "DEF-42",
                    "record_type": "defect",
                    "title": "数据不一致缺陷",
                    "display_title": "数据不一致缺陷",
                    "module": "area/A",
                    "severity": "一般",
                    "steps": ["步骤1", "步骤2"],
                    "expected": "",
                    "expected_resolution": "expected_missing_but_description_present",
                    "expected_source_section": "缺陷描述*",
                    "actual": "数据不一致",
                    "content_text": "数据不一致缺陷",
                    "quality_flags": ["missing_expected_section"],
                },
                schema_path=ROOT
                / "docs"
                / "knowledge"
                / "schemas"
                / "defect.schema.yaml",
            ),
            validate_normalized_record(
                record={
                    "id": "DEF-43",
                    "record_type": "defect",
                    "title": "销售渠道为空报错缺陷",
                    "display_title": "销售渠道为空报错缺陷",
                    "module": "area/A",
                    "severity": "一般",
                    "steps": ["步骤1", "步骤2"],
                    "expected": "",
                    "expected_resolution": "expected_missing_but_description_present",
                    "expected_source_section": "缺陷描述*",
                    "actual": "报错销售渠道为空",
                    "content_text": "销售渠道为空报错缺陷",
                    "quality_flags": ["missing_expected_section"],
                },
                schema_path=ROOT
                / "docs"
                / "knowledge"
                / "schemas"
                / "defect.schema.yaml",
            ),
        ]
        baseline_warning_count = sum(
            1 for item in baseline_validations if item["warnings"]
        )
        baseline_admissible_warning_count = sum(
            1
            for item in baseline_validations
            if any(
                detail.get("admission") == "admissible"
                for detail in item["warning_details"]
            )
        )
        baseline_warning_rate = baseline_warning_count / len(baseline_validations)

        importer = SymptomOnlyDefectImporter(
            defect_rows=[
                SheetRow(
                    row_number=5,
                    values={
                        "ID": "41",
                        "类型": "缺陷",
                        "标题": "导入失败缺陷",
                        "内容": "### 缺陷描述*\n导入失败，任务执行失败后无法继续\n### 重现步骤\n步骤1\n步骤2\n### 实际结果\n导入失败",
                        "状态": "待处理",
                        "严重程度": "一般",
                        "标签": "area/A",
                        "来源": "代码开发",
                        "环境": "测试",
                    },
                ),
                SheetRow(
                    row_number=6,
                    values={
                        "ID": "42",
                        "类型": "缺陷",
                        "标题": "数据不一致缺陷",
                        "内容": "### 缺陷描述*\n订单状态数据不一致，两个页面显示不一致\n### 重现步骤\n步骤1\n步骤2\n### 实际结果\n数据不一致",
                        "状态": "待处理",
                        "严重程度": "一般",
                        "标签": "area/A",
                        "来源": "代码开发",
                        "环境": "测试",
                    },
                ),
                SheetRow(
                    row_number=7,
                    values={
                        "ID": "43",
                        "类型": "缺陷",
                        "标题": "销售渠道为空报错缺陷",
                        "内容": "### 缺陷描述*\n报错销售渠道为空，保存流程中断\n### 重现步骤\n步骤1\n步骤2\n### 实际结果\n报错销售渠道为空",
                        "状态": "待处理",
                        "严重程度": "一般",
                        "标签": "area/A",
                        "来源": "代码开发",
                        "环境": "测试",
                    },
                ),
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_root = Path(tmp_dir)
            result = importer.export_small_batch(
                knowledge_root=out_root,
                defect_limit=3,
                testcase_limit=0,
            )

            report = yaml.safe_load(
                next(
                    (out_root / "imports" / "reports").glob("*-report.yaml")
                ).read_text()
            )

            self.assertNotIn("missing_expected", report["warning_code_distribution"])
            self.assertLess(result["warning_count"], baseline_warning_count)
            self.assertLess(
                result["admissible_warning_count"], baseline_admissible_warning_count
            )
            self.assertLess(result["warning_rate"], baseline_warning_rate)
            self.assertLess(report["quality_warning_count"], baseline_warning_count)
            self.assertLess(
                report["admissible_warning_count"], baseline_admissible_warning_count
            )

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

    def test_batch_gate_fails_when_blocking_warning_rate_exceeds_threshold(
        self,
    ) -> None:
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
