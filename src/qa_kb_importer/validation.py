from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


CORE_FIELDS_BY_RECORD_TYPE = {
    "defect": [
        "title",
        "display_title",
        "module",
        "severity",
        "steps",
        "expected",
        "actual",
        "content_text",
    ],
    "testcase": [
        "name",
        "display_title",
        "module",
        "steps",
        "expected",
        "priority",
        "content_text",
    ],
}

WARNING_DEFINITIONS = {
    "missing_display_title": {
        "severity": "warning",
        "message": "display_title is empty",
        "suggestion": "补充 display_title 字段",
        "category": "structural",
        "source_field": "display_title",
        "default_source_section": "",
        "default_admission": "blocking",
    },
    "missing_expected": {
        "severity": "warning",
        "message": "expected is empty",
        "suggestion": "补充 expected 字段",
        "category": "semantic",
        "source_field": "expected",
        "default_source_section": "",
        "default_admission": "blocking",
    },
    "missing_actual": {
        "severity": "warning",
        "message": "actual is empty",
        "suggestion": "补充 actual 字段",
        "category": "semantic",
        "source_field": "actual",
        "default_source_section": "实际结果",
        "default_admission": "blocking",
    },
    "missing_steps": {
        "severity": "warning",
        "message": "steps is empty",
        "suggestion": "补充 defect 复现步骤",
        "category": "semantic",
        "source_field": "steps",
        "default_source_section": "重现步骤",
        "default_admission": "blocking",
    },
    "steps_too_short": {
        "severity": "warning",
        "message": "steps are too short",
        "suggestion": "补充更完整的复现步骤",
        "category": "semantic",
        "source_field": "steps",
        "default_source_section": "重现步骤",
        "default_admission": "blocking",
    },
    "expected_actual_too_similar": {
        "severity": "warning",
        "message": "expected and actual are too similar",
        "suggestion": "区分期望结果与实际结果",
        "category": "semantic",
        "source_field": "expected",
        "default_source_section": "期望结果*",
        "default_admission": "blocking",
    },
    "testcase_expected_missing": {
        "severity": "warning",
        "message": "testcase expected is empty",
        "suggestion": "补充 testcase 预期结果",
        "category": "semantic",
        "source_field": "expected",
        "default_source_section": "步骤与结果/预期结果",
        "default_admission": "blocking",
    },
    "testcase_steps_missing": {
        "severity": "warning",
        "message": "testcase steps are empty",
        "suggestion": "补充 testcase 步骤",
        "category": "semantic",
        "source_field": "steps",
        "default_source_section": "步骤与结果/操作步骤",
        "default_admission": "blocking",
    },
    "testcase_steps_too_short": {
        "severity": "warning",
        "message": "testcase steps are too short",
        "suggestion": "补充 testcase 更完整的步骤描述",
        "category": "semantic",
        "source_field": "steps",
        "default_source_section": "步骤与结果/操作步骤",
        "default_admission": "admissible",
    },
    "question_like_record": {
        "severity": "warning",
        "message": "record appears to be a question or confirmation item",
        "suggestion": "确认是否应转为待确认事项，而不是直接作为 defect 收录",
        "category": "semantic",
        "source_field": "title",
        "default_source_section": "缺陷标题",
        "default_admission": "blocking",
    },
    "bundle_like_record": {
        "severity": "warning",
        "message": "record appears to bundle multiple issues or requirement-like notes",
        "suggestion": "拆分为独立 defect，或转为需求/确认事项",
        "category": "semantic",
        "source_field": "title",
        "default_source_section": "缺陷标题",
        "default_admission": "admissible",
    },
}


def load_schema(schema_path: Path | str) -> dict[str, Any]:
    payload = yaml.safe_load(Path(schema_path).read_text(encoding="utf-8"))
    return payload["schema"]


def validate_normalized_record(
    record: dict[str, Any], schema_path: Path | str
) -> dict[str, Any]:
    schema = load_schema(schema_path)
    errors: list[str] = []
    warnings: list[str] = []
    warning_codes: list[str] = []
    warning_details: list[dict[str, str]] = []

    missing_required = 0
    missing_display_title = 0
    missing_core = 0

    for field in schema.get("required", []):
        if field not in record:
            errors.append(f"missing required field: {field}")
            missing_required += 1

    for field_name, field_schema in schema.get("properties", {}).items():
        if field_name not in record:
            continue
        if not _matches_type(record[field_name], field_schema):
            expected_type = field_schema.get("type", "unknown")
            actual_type = type(record[field_name]).__name__
            errors.append(
                f"type mismatch for field {field_name}: expected {expected_type}, got {actual_type}"
            )

    display_title = str(record.get("display_title", "")).strip()
    if not display_title:
        errors.append("display_title is empty")
        missing_display_title += 1
        _append_warning(
            "missing_display_title", record, warnings, warning_codes, warning_details
        )

    record_type = record.get("record_type", schema.get("record_type"))
    for field in CORE_FIELDS_BY_RECORD_TYPE.get(record_type, []):
        if _is_empty_value(record.get(field)):
            warnings.append(f"core field is empty: {field}")
            missing_core += 1

    _append_semantic_warnings(
        record=record,
        record_type=record_type,
        warnings=warnings,
        warning_codes=warning_codes,
        warning_details=warning_details,
    )

    quality_flags = record.get("quality_flags", [])
    if not isinstance(quality_flags, list):
        quality_flags = []

    return {
        "record_id": record.get("id", ""),
        "record_type": record_type,
        "passed": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "warning_codes": warning_codes,
        "warning_details": warning_details,
        "metrics": {
            "missing_required_field_count": missing_required,
            "missing_display_title_count": missing_display_title,
            "missing_core_field_count": missing_core,
        },
        "quality_flags": quality_flags,
    }


def validate_normalized_directory(
    directory: Path | str, schema_path: Path | str
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in sorted(Path(directory).glob("*.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        result = validate_normalized_record(record=record, schema_path=schema_path)
        result["file_path"] = str(path)
        results.append(result)
    return results


def _matches_type(value: Any, schema: dict[str, Any]) -> bool:
    expected_type = schema.get("type")
    if expected_type is None:
        return True
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "array":
        if not isinstance(value, list):
            return False
        item_schema = schema.get("items")
        if not item_schema:
            return True
        return all(_matches_type(item, item_schema) for item in value)
    if expected_type == "object":
        if not isinstance(value, dict):
            return False
        for field in schema.get("required", []):
            if field not in value:
                return False
        for field_name, field_schema in schema.get("properties", {}).items():
            if field_name in value and not _matches_type(
                value[field_name], field_schema
            ):
                return False
        return True
    return True


def _is_empty_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0 or all(_is_empty_value(item) for item in value)
    return False


def _append_semantic_warnings(
    record: dict[str, Any],
    record_type: Any,
    warnings: list[str],
    warning_codes: list[str],
    warning_details: list[dict[str, str]],
) -> None:
    if record_type == "defect":
        steps = record.get("steps", [])
        expected = record.get("expected", "")
        actual = record.get("actual", "")
        if _is_question_like_record(record):
            _append_warning(
                "question_like_record",
                record,
                warnings,
                warning_codes,
                warning_details,
            )
            return
        if _is_bundle_like_record(record):
            _append_warning(
                "bundle_like_record",
                record,
                warnings,
                warning_codes,
                warning_details,
            )
            return
        if _is_empty_value(steps):
            _append_warning(
                "missing_steps", record, warnings, warning_codes, warning_details
            )
        elif (
            isinstance(steps, list)
            and len(steps) == 1
            and len(str(steps[0]).strip()) < 10
        ):
            _append_warning(
                "steps_too_short", record, warnings, warning_codes, warning_details
            )
        if _is_empty_value(expected):
            _append_warning(
                "missing_expected", record, warnings, warning_codes, warning_details
            )
        if _is_empty_value(actual):
            _append_warning(
                "missing_actual", record, warnings, warning_codes, warning_details
            )
        if not _is_empty_value(expected) and not _is_empty_value(actual):
            if _normalize_text(expected) == _normalize_text(actual):
                _append_warning(
                    "expected_actual_too_similar",
                    record,
                    warnings,
                    warning_codes,
                    warning_details,
                )
        return

    if record_type == "testcase":
        steps = record.get("steps", [])
        expected = record.get("expected", "")
        if _is_empty_value(steps):
            _append_warning(
                "testcase_steps_missing",
                record,
                warnings,
                warning_codes,
                warning_details,
            )
        elif (
            isinstance(steps, list)
            and len(steps) == 1
            and len(str(steps[0]).strip()) < 10
        ):
            _append_warning(
                "testcase_steps_too_short",
                record,
                warnings,
                warning_codes,
                warning_details,
            )
        if _is_empty_value(expected):
            _append_warning(
                "testcase_expected_missing",
                record,
                warnings,
                warning_codes,
                warning_details,
            )


def _append_warning(
    code: str,
    record: dict[str, Any],
    warnings: list[str],
    warning_codes: list[str],
    warning_details: list[dict[str, str]],
) -> None:
    if code in warning_codes:
        return
    definition = WARNING_DEFINITIONS[code]
    warnings.append(definition["message"])
    warning_codes.append(code)
    warning_details.append(
        {
            "code": code,
            "severity": definition["severity"],
            "message": definition["message"],
            "suggestion": definition["suggestion"],
            "category": definition["category"],
            "source_field": definition["source_field"],
            "source_section": _resolve_source_section(code, record, definition),
            "admission": _resolve_admission(code, record, definition),
        }
    )


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).split()).strip().lower()


def _match_record_scope(record: dict[str, Any], tokens: tuple[str, ...]) -> str | None:
    title = _normalize_text(
        " ".join(
            str(part)
            for part in (record.get("title", ""), record.get("display_title", ""))
            if str(part).strip()
        )
    )
    if title and any(token in title for token in tokens):
        return "缺陷标题"

    content = _normalize_text(record.get("content_text", ""))
    if content and any(token in content for token in tokens):
        return "缺陷描述*"

    return None


def _question_like_source_section(record: dict[str, Any]) -> str | None:
    return _match_record_scope(
        record, ("？", "?", "能否", "是否", "请确认", "需要确认", "待确认")
    )


def _bundle_like_source_section(record: dict[str, Any]) -> str | None:
    return _match_record_scope(
        record, ("问题若干", "问题集合", "布局调整", "需要产品确认")
    )


def _is_question_like_record(record: dict[str, Any]) -> bool:
    if not _is_empty_value(record.get("expected")):
        return False
    if not _is_empty_value(record.get("actual")):
        return False
    return _question_like_source_section(record) is not None


def _is_bundle_like_record(record: dict[str, Any]) -> bool:
    if not _is_empty_value(record.get("expected")):
        return False
    return _bundle_like_source_section(record) is not None


def _resolve_source_section(
    code: str, record: dict[str, Any], definition: dict[str, str]
) -> str:
    if code == "missing_expected":
        return str(record.get("expected_source_section", "")).strip()
    if code == "question_like_record":
        return _question_like_source_section(record) or definition.get(
            "default_source_section", ""
        )
    if code == "bundle_like_record":
        return _bundle_like_source_section(record) or definition.get(
            "default_source_section", ""
        )
    return definition.get("default_source_section", "")


def _resolve_admission(
    code: str, record: dict[str, Any], definition: dict[str, str]
) -> str:
    if code == "missing_expected":
        resolution = record.get("expected_resolution")
        if resolution == "expected_missing_but_description_present":
            return "admissible"
        if resolution == "expected_missing_unrecoverable":
            return "blocking"
    return definition.get("default_admission", "blocking")
