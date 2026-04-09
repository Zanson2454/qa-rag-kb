from __future__ import annotations

from collections import Counter
from typing import Any


def determine_batch_gate(
    schema_fail_count: int,
    error_count: int,
    admissible_warning_count: int,
    blocking_warning_count: int,
    record_count: int,
) -> str:
    if schema_fail_count > 0 or error_count > 0:
        return "failed"
    if record_count > 0 and blocking_warning_count / record_count > 0.30:
        return "failed"
    if record_count > 0 and admissible_warning_count / record_count > 0.10:
        return "warning"
    return "passed"


def build_batch_quality_report(
    batch_id: str,
    source_type: str,
    manifest: dict[str, Any],
    error_list: dict[str, Any],
    validation_results: list[dict[str, Any]],
    details_file: str,
    testcase_step_row_count_before_grouping: int,
    testcase_case_count_after_grouping: int,
) -> dict[str, Any]:
    schema_fail_count = sum(1 for item in validation_results if not item["passed"])
    schema_pass_count = len(validation_results) - schema_fail_count
    quality_warning_count = sum(1 for item in validation_results if item["warnings"])
    semantic_warning_count = sum(
        1
        for item in validation_results
        if any(detail.get("category") == "semantic" for detail in item.get("warning_details", []))
    )
    admissible_warning_count = sum(
        1
        for item in validation_results
        if any(detail.get("admission") == "admissible" for detail in item.get("warning_details", []))
    )
    blocking_warning_count = sum(
        1
        for item in validation_results
        if any(detail.get("admission") == "blocking" for detail in item.get("warning_details", []))
    )
    error_count = len(error_list.get("errors", []))
    flag_counter = Counter()
    warning_code_counter = Counter()
    warning_severity_counter = Counter()
    admission_counter = Counter()
    for item in validation_results:
        flag_counter.update(item.get("quality_flags", []))
        warning_code_counter.update(item.get("warning_codes", []))
        warning_severity_counter.update(
            detail.get("severity", "warning") for detail in item.get("warning_details", [])
        )
        admission_counter.update(detail.get("admission", "blocking") for detail in item.get("warning_details", []))

    missing_required_field_count = sum(item["metrics"]["missing_required_field_count"] for item in validation_results)
    missing_display_title_count = sum(item["metrics"]["missing_display_title_count"] for item in validation_results)
    missing_core_field_count = sum(item["metrics"]["missing_core_field_count"] for item in validation_results)
    record_count = len(validation_results)
    warning_rate = quality_warning_count / record_count if record_count else 0.0
    semantic_warning_rate = semantic_warning_count / record_count if record_count else 0.0
    admissible_warning_rate = admissible_warning_count / record_count if record_count else 0.0
    blocking_warning_rate = blocking_warning_count / record_count if record_count else 0.0

    gate = determine_batch_gate(
        schema_fail_count=schema_fail_count,
        error_count=error_count,
        admissible_warning_count=admissible_warning_count,
        blocking_warning_count=blocking_warning_count,
        record_count=record_count,
    )

    return {
        "batch_id": batch_id,
        "source_type": source_type,
        "input_record_count": manifest.get("defect_count", 0) + manifest.get("testcase_count", 0),
        "success_output_count": len(validation_results),
        "error_count": error_count,
        "schema_pass_count": schema_pass_count,
        "schema_fail_count": schema_fail_count,
        "missing_required_field_count": missing_required_field_count,
        "missing_display_title_count": missing_display_title_count,
        "missing_core_field_count": missing_core_field_count,
        "quality_warning_count": quality_warning_count,
        "semantic_warning_count": semantic_warning_count,
        "admissible_warning_count": admissible_warning_count,
        "blocking_warning_count": blocking_warning_count,
        "warning_rate": round(warning_rate, 4),
        "semantic_warning_rate": round(semantic_warning_rate, 4),
        "admissible_warning_rate": round(admissible_warning_rate, 4),
        "blocking_warning_rate": round(blocking_warning_rate, 4),
        "warning_code_distribution": dict(warning_code_counter),
        "warning_severity_distribution": dict(warning_severity_counter),
        "admission_distribution": dict(admission_counter),
        "quality_flag_distribution": dict(flag_counter),
        "testcase_step_row_count_before_grouping": testcase_step_row_count_before_grouping,
        "testcase_case_count_after_grouping": testcase_case_count_after_grouping,
        "quality_status": "warning" if quality_warning_count > 0 else "clean",
        "gate": gate,
        "details_file": details_file,
        "failed_reason": _build_failed_reason(gate, schema_fail_count, error_count, blocking_warning_rate),
        "warning_summary": _build_warning_summary(
            admissible_warning_count=admissible_warning_count,
            blocking_warning_count=blocking_warning_count,
            record_count=record_count,
        ),
        "advice": _build_advice(gate),
    }


def _build_failed_reason(gate: str, schema_fail_count: int, error_count: int, blocking_warning_rate: float) -> str:
    if gate != "failed":
        return ""
    if schema_fail_count > 0:
        return "schema validation failed"
    if error_count > 0:
        return "import errors exist"
    if blocking_warning_rate > 0.30:
        return "blocking warning rate exceeds 0.30"
    return "gate failed"


def _build_warning_summary(admissible_warning_count: int, blocking_warning_count: int, record_count: int) -> str:
    if record_count == 0:
        return "no records"
    return (
        f"admissible warnings: {admissible_warning_count}/{record_count}, "
        f"blocking warnings: {blocking_warning_count}/{record_count}"
    )


def _build_advice(gate: str) -> str:
    if gate == "failed":
        return "先修复 schema fail、import error 或高占比语义 warning，再进入下一阶段。"
    if gate == "warning":
        return "可以保留当前批次作为验收样本，但应继续收敛 warning 分类。"
    return "当前批次质量稳定，可作为 Phase 1 验收证据。"
