from __future__ import annotations

import shutil
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import yaml

from .quality import build_batch_quality_report
from .validation import validate_normalized_directory

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"

DEFECT_ALLOWED_SOURCES = {
    "代码开发",
    "需求调研",
    "部署实施",
    "需求设计",
    "技术设计",
    "UI设计",
}

SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "docs" / "knowledge" / "schemas"


@dataclass
class SheetRow:
    row_number: int
    values: dict[str, str]


class FixedTemplateImporter:
    def __init__(self, defect_file: Path | str, testcase_file: Path | str) -> None:
        self.defect_file = Path(defect_file)
        self.testcase_file = Path(testcase_file)

    def import_defects(self, limit: int = 3) -> list[dict[str, Any]]:
        return [item["record"] for item in self._collect_defect_records(limit=limit)]

    def import_testcases(self, limit: int = 3) -> list[dict[str, Any]]:
        return [item["record"] for item in self._collect_testcase_records(limit=limit)]

    def export_small_batch(
        self,
        knowledge_root: Path | str,
        defect_limit: int = 3,
        testcase_limit: int = 3,
    ) -> dict[str, Any]:
        root = Path(knowledge_root)
        layout = self._prepare_export_layout(root)
        import_batch_id = self._build_import_batch_id()
        created_at = datetime.now(timezone.utc).isoformat()
        errors: list[dict[str, Any]] = []

        raw_defect_path = layout["raw_defects"] / f"{import_batch_id}-{self.defect_file.name}"
        raw_testcase_path = layout["raw_testcases"] / f"{import_batch_id}-{self.testcase_file.name}"
        shutil.copy2(self.defect_file, raw_defect_path)
        shutil.copy2(self.testcase_file, raw_testcase_path)

        defects = self._collect_defect_records(limit=defect_limit, errors=errors)
        testcases = self._collect_testcase_records(limit=testcase_limit, errors=errors)
        testcase_step_row_count_before_grouping = sum(len(case["snapshot"]["entries"]) for case in testcases)
        testcase_case_count_after_grouping = len(testcases)
        conflict_count = 0

        for item in defects:
            normalized_path = layout["normalized_defects"] / f"{item['record']['id']}.yaml"
            snapshot_path = layout["snapshot_defects"] / f"{item['record']['id']}.yaml"
            if normalized_path.exists():
                conflict_count += 1
                errors.append(
                    self._build_error_entry(
                        record=item["record"],
                        error_type="target_conflict",
                        error_message=f"normalized target already exists: {normalized_path.name}",
                        raw_excerpt=item["snapshot"]["raw_values"],
                    )
                )
                continue
            self._write_yaml(normalized_path, item["record"])
            self._write_yaml(snapshot_path, item["snapshot"])

        for item in testcases:
            normalized_path = layout["normalized_testcases"] / f"{item['record']['id']}.yaml"
            snapshot_path = layout["snapshot_testcases"] / f"{item['record']['id']}.yaml"
            if normalized_path.exists():
                conflict_count += 1
                errors.append(
                    self._build_error_entry(
                        record=item["record"],
                        error_type="target_conflict",
                        error_message=f"normalized target already exists: {normalized_path.name}",
                        raw_excerpt=item["snapshot"]["header"],
                    )
                )
                continue
            self._write_yaml(normalized_path, item["record"])
            self._write_yaml(snapshot_path, item["snapshot"])

        success_count = len(defects) + len(testcases) - conflict_count
        failure_count = len(errors)

        manifest = {
            "import_batch_id": import_batch_id,
            "created_at": created_at,
            "inputs": {
                "defect_file": self.defect_file.name,
                "testcase_file": self.testcase_file.name,
                "raw_defect_path": str(raw_defect_path.relative_to(root)),
                "raw_testcase_path": str(raw_testcase_path.relative_to(root)),
            },
            "defect_count": len(defects),
            "testcase_count": len(testcases),
            "error_count": len(errors),
            "success_count": success_count,
            "failure_count": failure_count,
            "conflict_count": conflict_count,
            "warning_count": sum(len(item["record"]["quality_flags"]) for item in defects + testcases),
        }
        error_payload = {
            "import_batch_id": import_batch_id,
            "created_at": created_at,
            "errors": errors,
        }

        manifest_path = layout["manifests"] / f"{import_batch_id}.yaml"
        error_list_path = layout["errors"] / f"{import_batch_id}.yaml"
        self._write_yaml(manifest_path, manifest)
        self._write_yaml(error_list_path, error_payload)

        validation_results = []
        validation_results.extend(
            validate_normalized_directory(
                directory=layout["normalized_defects"],
                schema_path=SCHEMA_ROOT / "defect.schema.yaml",
            )
        )
        validation_results.extend(
            validate_normalized_directory(
                directory=layout["normalized_testcases"],
                schema_path=SCHEMA_ROOT / "testcase.schema.yaml",
            )
        )

        details_payload = {
            "batch_id": import_batch_id,
            "records": validation_results,
        }
        validation_details_path = layout["reports"] / f"{import_batch_id}-validation-details.yaml"
        self._write_yaml(validation_details_path, details_payload)

        report = build_batch_quality_report(
            batch_id=import_batch_id,
            source_type="excel",
            manifest=manifest,
            error_list=error_payload,
            validation_results=validation_results,
            details_file=str(validation_details_path),
            testcase_step_row_count_before_grouping=testcase_step_row_count_before_grouping,
            testcase_case_count_after_grouping=testcase_case_count_after_grouping,
        )
        report_path = layout["reports"] / f"{import_batch_id}-report.yaml"
        self._write_yaml(report_path, report)

        return {
            "import_batch_id": import_batch_id,
            "defect_count": len(defects),
            "testcase_count": len(testcases),
            "error_count": len(errors),
            "success_count": success_count,
            "failure_count": failure_count,
            "conflict_count": conflict_count,
            "gate": report["gate"],
            "warning_count": report["quality_warning_count"],
            "schema_fail_count": report["schema_fail_count"],
            "quality_warning_count": report["quality_warning_count"],
            "semantic_warning_count": report["semantic_warning_count"],
            "admissible_warning_count": report["admissible_warning_count"],
            "blocking_warning_count": report["blocking_warning_count"],
            "warning_rate": report["warning_rate"],
            "manifest_path": str(manifest_path),
            "error_list_path": str(error_list_path),
            "report_path": str(report_path),
            "validation_details_path": str(validation_details_path),
        }

    def _build_error_entry(
        self,
        record: dict[str, Any],
        error_type: str,
        error_message: str,
        raw_excerpt: dict[str, Any],
    ) -> dict[str, Any]:
        source = record.get("source", {})
        return {
            "source_file": source.get("source_file", ""),
            "source_sheet": source.get("source_sheet", ""),
            "source_row": source.get("source_row", 0),
            "source_id": source.get("source_id", ""),
            "error_type": error_type,
            "error_message": error_message,
            "raw_excerpt": self._render_raw_excerpt(raw_excerpt),
        }

    def _render_raw_excerpt(self, raw_excerpt: dict[str, Any]) -> str:
        return yaml.safe_dump(raw_excerpt, allow_unicode=True, sort_keys=False).strip()

    def _write_yaml(self, path: Path, payload: dict[str, Any]) -> None:
        path.write_text(
            yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    def _prepare_export_layout(self, root: Path) -> dict[str, Path]:
        layout = {
            "raw_defects": root / "imports" / "raw" / "defects",
            "raw_testcases": root / "imports" / "raw" / "testcases",
            "manifests": root / "imports" / "manifests",
            "errors": root / "imports" / "errors",
            "reports": root / "imports" / "reports",
            "snapshot_defects": root / "snapshots" / "defects",
            "snapshot_testcases": root / "snapshots" / "testcases",
            "normalized_defects": root / "normalized" / "defects",
            "normalized_testcases": root / "normalized" / "testcases",
        }
        for path in layout.values():
            path.mkdir(parents=True, exist_ok=True)
        return layout

    def _build_import_batch_id(self) -> str:
        return datetime.now(timezone.utc).strftime("batch-%Y%m%dT%H%M%SZ")

    def _collect_defect_records(self, limit: int, errors: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        rows = self._read_defect_rows()
        defects: list[dict[str, Any]] = []
        seen_source_ids: set[str] = set()
        for row in rows:
            if row.values.get("类型") != "缺陷":
                continue
            defect = self._normalize_defect(row)
            source_id = defect["source"]["source_id"]
            if source_id in seen_source_ids:
                if errors is not None:
                    errors.append(
                        self._build_error_entry(
                            record=defect,
                            error_type="duplicate_source_id",
                            error_message=f"duplicate source_id in current batch: {source_id}",
                            raw_excerpt=row.values,
                        )
                    )
                continue
            seen_source_ids.add(source_id)
            if not defect["steps"]:
                continue
            defects.append(
                {
                    "record": defect,
                    "snapshot": {
                        "record_type": "defect",
                        "record_id": defect["id"],
                        "source_row": row.row_number,
                        "raw_values": row.values,
                        "normalized_fields": {
                            "title": defect["title"],
                            "module": defect["module"],
                            "severity": defect["severity"],
                            "quality_flags": defect["quality_flags"],
                        },
                    },
                }
            )
            if len(defects) >= limit:
                break
        return defects

    def _collect_testcase_records(
        self,
        limit: int,
        errors: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        cases = self._read_testcase_cases()
        testcases: list[dict[str, Any]] = []
        seen_source_ids: set[str] = set()
        for case in cases[:limit]:
            testcase = self._normalize_testcase(case)
            source_id = testcase["source"]["source_id"]
            if source_id in seen_source_ids:
                if errors is not None:
                    errors.append(
                        self._build_error_entry(
                            record=testcase,
                            error_type="duplicate_source_id",
                            error_message=f"duplicate source_id in current batch: {source_id}",
                            raw_excerpt=case["header"],
                        )
                    )
                continue
            seen_source_ids.add(source_id)
            testcases.append(
                {
                    "record": testcase,
                    "snapshot": {
                        "record_type": "testcase",
                        "record_id": testcase["id"],
                        "source_row": case["row_number"],
                        "header": case["header"],
                        "entries": case["entries"],
                        "normalized_fields": {
                            "name": testcase["name"],
                            "module": testcase["module"],
                            "priority": testcase["priority"],
                            "quality_flags": testcase["quality_flags"],
                        },
                    },
                }
            )
        return testcases

    def _normalize_defect(self, row: SheetRow) -> dict[str, Any]:
        title = self._clean_text(row.values.get("标题", ""))
        content = row.values.get("内容", "")
        tags = self._split_csv(row.values.get("标签", ""))
        module = self._derive_defect_module(tags)
        sections = self._extract_markdown_sections(content)
        quality_flags: list[str] = []

        if not self._clean_text(content):
            quality_flags.append("missing_content")

        steps_text = self._clean_multiline(sections.get("重现步骤", ""))
        if steps_text:
            steps = self._split_lines(steps_text)
        else:
            description = self._clean_multiline(sections.get("缺陷描述*", ""))
            steps = self._split_lines(description)
            if steps:
                quality_flags.append("steps_fallback_from_description")

        expected = self._clean_multiline(sections.get("期望结果*", ""))
        expected_resolution = "expected_section_present"
        expected_source_section = "期望结果*"
        if not expected:
            description = self._clean_multiline(sections.get("缺陷描述*", ""))
            recovered_expected = self._recover_defect_expected_candidate(
                title=title,
                description=description,
            )
            if recovered_expected is not None:
                expected = recovered_expected["expected_candidate"]
                expected_resolution = recovered_expected["expected_resolution"]
                expected_source_section = recovered_expected["expected_source_section"]
                quality_flags.append("generated_expected_candidate")
            else:
                quality_flags.append("missing_expected_section")
                if description:
                    expected_resolution = "expected_missing_but_description_present"
                    expected_source_section = "缺陷描述*"
                else:
                    expected_resolution = "expected_missing_unrecoverable"
                    expected_source_section = ""
        actual = self._clean_multiline(sections.get("实际结果", ""))
        if not actual:
            actual = self._clean_multiline(sections.get("缺陷描述*", ""))
            if actual:
                quality_flags.append("missing_actual_section")
            else:
                quality_flags.append("missing_actual_section")

        source_value = self._clean_text(row.values.get("来源", ""))
        if source_value and source_value not in DEFECT_ALLOWED_SOURCES:
            quality_flags.append("source_value_needs_normalization")
        if module == "unknown":
            quality_flags.append("unknown_module")

        content_text = self._render_defect_content_text(
            title=title,
            module=module,
            severity=self._clean_text(row.values.get("严重程度", "")),
            status=self._clean_text(row.values.get("状态", "")),
            environment=self._clean_text(row.values.get("环境", "")),
            steps=steps,
            actual=actual,
            expected=expected,
        )

        source_id = self._clean_text(row.values.get("ID", ""))
        return {
            "id": f"DEF-{source_id}",
            "record_type": "defect",
            "title": title,
            "display_title": title,
            "module": module,
            "severity": self._clean_text(row.values.get("严重程度", "")),
            "steps": steps,
            "expected": expected,
            "expected_resolution": expected_resolution,
            "expected_source_section": expected_source_section,
            "actual": actual,
            "tags": tags,
            "content_text": content_text,
            "quality_flags": self._dedupe_flags(quality_flags),
            "source": {
                "source_type": "excel",
                "source_id": source_id,
                "source_file": self.defect_file.name,
                "source_sheet": "issue",
                "source_row": row.row_number,
            },
            "version": 1,
        }

    def _recover_defect_expected_candidate(
        self, title: str, description: str
    ) -> dict[str, str] | None:
        for source_section, text in (
            ("缺陷描述*", description),
            ("缺陷标题", title),
        ):
            candidate = self._build_expected_candidate_from_symptom(text)
            if candidate:
                return {
                    "expected_candidate": candidate,
                    "expected_resolution": "expected_generated_from_symptom",
                    "expected_source_section": source_section,
                }
        return None

    def _build_expected_candidate_from_symptom(self, text: str) -> str | None:
        normalized = self._clean_multiline(text)
        if not normalized:
            return None

        if self._has_empty_error_symptom(normalized):
            subject = self._extract_empty_error_subject(normalized)
            if subject:
                return f"不应报错{subject}"
            return "不应报错为空"

        if self._has_inconsistency_symptom(normalized):
            return "相关结果应一致"

        if self._has_failure_symptom(normalized):
            return "操作应成功，不应失败"

        return None

    def _has_failure_symptom(self, text: str) -> bool:
        return "失败" in text

    def _has_inconsistency_symptom(self, text: str) -> bool:
        return "不一致" in text

    def _has_empty_error_symptom(self, text: str) -> bool:
        return "报错" in text and "为空" in text

    def _extract_empty_error_subject(self, text: str) -> str:
        match = re.search(r"报错\s*([^\n，。；;]{1,40}?为空)", text)
        if match:
            return self._clean_text(match.group(1))
        match = re.search(r"([^\n，。；;]{1,40}?为空)", text)
        if match and "报错" in match.group(1):
            return self._clean_text(match.group(1).removeprefix("报错"))
        if "报错" in text:
            tail = text.split("报错", 1)[1].strip(" ，。；;\n")
            if tail:
                return tail[:40]
        return ""

    def _normalize_testcase(self, case: dict[str, Any]) -> dict[str, Any]:
        name = self._clean_text(case["header"].get("用例名称", ""))
        priority = self._clean_text(case["header"].get("优先级", ""))
        testset = self._clean_text(case["header"].get("测试集", ""))
        preconditions = self._split_lines(case["header"].get("前置条件", ""))
        quality_flags: list[str] = []
        if not preconditions:
            quality_flags.append("missing_preconditions")

        steps: list[str] = []
        expected_parts: list[str] = []
        for entry in case["entries"]:
            step = self._clean_text(entry.get("步骤与结果/操作步骤", ""))
            expected = self._clean_text(entry.get("步骤与结果/预期结果", ""))
            if step:
                steps.append(step)
            else:
                quality_flags.append("empty_step_row")
            if expected:
                expected_parts.append(expected)
            else:
                quality_flags.append("missing_expected_step")

        expected = "\n".join(expected_parts)
        module = self._derive_testcase_module(testset)
        tags = self._derive_testcase_tags(testset, priority)
        content_text = self._render_testcase_content_text(
            name=name,
            module=module,
            preconditions=preconditions,
            steps=steps,
            expected_parts=expected_parts,
        )
        source_id = self._clean_text(case["header"].get("用例编号", ""))

        return {
            "id": f"TC-{source_id}",
            "record_type": "testcase",
            "name": name,
            "display_title": name,
            "module": module,
            "preconditions": preconditions,
            "steps": steps,
            "expected": expected,
            "priority": priority,
            "tags": tags,
            "content_text": content_text,
            "quality_flags": self._dedupe_flags(quality_flags),
            "source": {
                "source_type": "excel",
                "source_id": source_id,
                "source_file": self.testcase_file.name,
                "source_sheet": "测试用例.xlsx",
                "source_row": case["row_number"],
            },
            "version": 1,
        }

    def _read_defect_rows(self) -> list[SheetRow]:
        workbook = _XlsxXmlWorkbook(self.defect_file)
        rows = workbook.read_sheet("issue")
        headers = rows[2].values
        self._validate_columns(
            headers,
            ["ID", "类型", "标题", "内容", "状态", "严重程度", "标签", "来源", "环境"],
        )
        return [SheetRow(row.row_number, self._row_values(headers, row.values)) for row in rows[3:]]

    def _read_testcase_cases(self) -> list[dict[str, Any]]:
        workbook = _XlsxXmlWorkbook(self.testcase_file)
        rows = workbook.read_sheet("测试用例.xlsx")
        headers = self._combine_testcase_headers(rows[0].values, rows[1].values)
        self._validate_columns(
            headers,
            ["用例编号", "用例名称", "测试集", "优先级", "前置条件", "步骤与结果/操作步骤", "步骤与结果/预期结果"],
        )

        cases: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        for row in rows[2:]:
            mapped = self._row_values(headers, row.values)
            case_id = self._clean_text(mapped.get("用例编号", ""))
            if case_id:
                current = {
                    "row_number": row.row_number,
                    "header": mapped,
                    "entries": [mapped],
                }
                cases.append(current)
                continue

            if current is None:
                continue
            current["entries"].append(mapped)

        return cases

    def _combine_testcase_headers(self, top: list[str], sub: list[str]) -> list[str]:
        headers: list[str] = []
        width = max(len(top), len(sub))
        current_group = ""
        for index in range(width):
            top_value = self._clean_text(top[index] if index < len(top) else "")
            sub_value = self._clean_text(sub[index] if index < len(sub) else "")
            if top_value:
                current_group = top_value
            if top_value and sub_value:
                headers.append(f"{top_value}/{sub_value}")
            elif not top_value and sub_value and current_group:
                headers.append(f"{current_group}/{sub_value}")
            elif top_value:
                headers.append(top_value)
            else:
                headers.append(sub_value)
        return headers

    def _validate_columns(self, headers: list[str], required: list[str]) -> None:
        missing = [name for name in required if name not in headers]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _row_values(self, headers: list[str], values: list[str]) -> dict[str, str]:
        padded = values + [""] * (len(headers) - len(values))
        return {headers[index]: padded[index] for index in range(len(headers))}

    def _extract_markdown_sections(self, content: str) -> dict[str, str]:
        sections: dict[str, str] = {}
        current: str | None = None
        buffer: list[str] = []
        for line in content.splitlines():
            heading = re.match(r"^###\s*(.+?)\s*$", line.strip())
            if heading:
                if current is not None:
                    sections[current] = "\n".join(buffer).strip()
                current = heading.group(1)
                buffer = []
                continue
            if current is not None:
                buffer.append(line)
        if current is not None:
            sections[current] = "\n".join(buffer).strip()
        return sections

    def _clean_multiline(self, text: str) -> str:
        lines = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("![") and "](" in line:
                continue
            lines.append(line)
        return "\n".join(lines).strip()

    def _split_lines(self, text: str) -> list[str]:
        return [line.strip() for line in text.splitlines() if line.strip()]

    def _split_csv(self, text: str) -> list[str]:
        return [part.strip() for part in text.split(",") if part.strip()]

    def _derive_defect_module(self, tags: list[str]) -> str:
        for tag in tags:
            if tag.startswith("area/"):
                return tag.removeprefix("area/")
        return "unknown"

    def _derive_testcase_module(self, testset: str) -> str:
        parts = [part.strip() for part in testset.split("/") if part.strip()]
        if len(parts) >= 2:
            return "/".join(parts[:2])
        if parts:
            return parts[-1]
        return "unknown"

    def _derive_testcase_tags(self, testset: str, priority: str) -> list[str]:
        parts = [part.strip() for part in testset.split("/") if part.strip()]
        if priority:
            parts.append(f"priority/{priority}")
        return parts

    def _render_defect_content_text(
        self,
        title: str,
        module: str,
        severity: str,
        status: str,
        environment: str,
        steps: list[str],
        actual: str,
        expected: str,
    ) -> str:
        lines = [
            f"缺陷标题：{title}",
            f"统一标题：{title}",
            f"模块：{module}",
            f"严重度：{severity}",
            f"状态：{status}",
            f"环境：{environment}",
            "复现步骤：",
        ]
        for index, step in enumerate(steps, start=1):
            lines.append(f"{index}. {step}")
        lines.append("实际结果：")
        if actual:
            lines.extend(actual.splitlines())
        lines.append("期望结果：")
        if expected:
            lines.extend(expected.splitlines())
        else:
            lines.append("原始 Excel 未提供结构化期望结果段。")
        return "\n".join(lines)

    def _render_testcase_content_text(
        self,
        name: str,
        module: str,
        preconditions: list[str],
        steps: list[str],
        expected_parts: list[str],
    ) -> str:
        lines = [
            f"用例名称：{name}",
            f"统一标题：{name}",
            f"模块：{module}",
            "前置条件：",
        ]
        for index, item in enumerate(preconditions, start=1):
            lines.append(f"{index}. {item}")
        lines.append("测试步骤：")
        for index, step in enumerate(steps, start=1):
            lines.append(f"{index}. {step}")
        lines.append("预期结果：")
        for index, item in enumerate(expected_parts, start=1):
            lines.append(f"{index}. {item}")
        return "\n".join(lines)

    def _clean_text(self, value: Any) -> str:
        return str(value).strip() if value is not None else ""

    def _dedupe_flags(self, flags: list[str]) -> list[str]:
        out: list[str] = []
        for flag in flags:
            if flag and flag not in out:
                out.append(flag)
        return out


class _XlsxXmlWorkbook:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)

    def read_sheet(self, sheet_name: str) -> list[SheetRow]:
        with zipfile.ZipFile(self.path) as archive:
            shared = self._read_shared_strings(archive)
            target = self._sheet_target(archive, sheet_name)
            root = ET.fromstring(archive.read(target))
            sheet_data = root.find(f"{{{NS_MAIN}}}sheetData")
            if sheet_data is None:
                return []

            rows: list[SheetRow] = []
            for row in sheet_data.findall(f"{{{NS_MAIN}}}row"):
                row_number = int(row.attrib.get("r", "0"))
                cells: dict[int, str] = {}
                for cell in row.findall(f"{{{NS_MAIN}}}c"):
                    cells[self._column_index(cell.attrib.get("r", ""))] = self._cell_value(cell, shared)
                max_col = max(cells.keys(), default=0)
                values = [cells.get(index, "") for index in range(1, max_col + 1)]
                rows.append(SheetRow(row_number=row_number, values=values))
            return rows

    def _read_shared_strings(self, archive: zipfile.ZipFile) -> list[str]:
        try:
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        except KeyError:
            return []
        values: list[str] = []
        for item in root.findall(f"{{{NS_MAIN}}}si"):
            values.append("".join(node.text or "" for node in item.iter(f"{{{NS_MAIN}}}t")))
        return values

    def _sheet_target(self, archive: zipfile.ZipFile, sheet_name: str) -> str:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall(f"{{{NS_PKG_REL}}}Relationship")}
        sheets = workbook.find(f"{{{NS_MAIN}}}sheets")
        if sheets is None:
            raise ValueError("Workbook missing sheets")
        for sheet in sheets:
            if sheet.attrib.get("name") == sheet_name:
                rel_id = sheet.attrib[f"{{{NS_REL}}}id"]
                return f"xl/{rel_map[rel_id]}"
        raise ValueError(f"Sheet not found: {sheet_name}")

    def _cell_value(self, cell: ET.Element, shared_strings: list[str]) -> str:
        cell_type = cell.attrib.get("t")
        value_node = cell.find(f"{{{NS_MAIN}}}v")
        inline_node = cell.find(f"{{{NS_MAIN}}}is")
        if cell_type == "s" and value_node is not None and value_node.text is not None:
            return shared_strings[int(value_node.text)]
        if cell_type == "inlineStr" and inline_node is not None:
            return "".join(node.text or "" for node in inline_node.iter(f"{{{NS_MAIN}}}t"))
        if value_node is not None and value_node.text is not None:
            return value_node.text
        return ""

    def _column_index(self, cell_ref: str) -> int:
        letters = "".join(char for char in cell_ref if char.isalpha())
        index = 0
        for char in letters:
            index = index * 26 + ord(char) - 64
        return index
