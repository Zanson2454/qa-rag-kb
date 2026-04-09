from __future__ import annotations

import argparse
from pathlib import Path

from .importer import FixedTemplateImporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="固定模板版最小 Excel 导入器")
    parser.add_argument(
        "--defect-file",
        default="input/issue-export-20260408.xlsx",
        help="固定模板 defect Excel 路径",
    )
    parser.add_argument(
        "--testcase-file",
        default="input/测试用例-scm-20260408.xlsx",
        help="固定模板 testcase Excel 路径",
    )
    parser.add_argument(
        "--knowledge-root",
        default="docs/knowledge",
        help="Phase 1 知识库根目录",
    )
    parser.add_argument("--defect-limit", type=int, default=3, help="导出的 defect 数量")
    parser.add_argument("--testcase-limit", type=int, default=3, help="导出的 testcase 数量")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    importer = FixedTemplateImporter(
        defect_file=Path(args.defect_file),
        testcase_file=Path(args.testcase_file),
    )
    result = importer.export_small_batch(
        knowledge_root=Path(args.knowledge_root),
        defect_limit=args.defect_limit,
        testcase_limit=args.testcase_limit,
    )
    print(
        f"batch={result['import_batch_id']} defects={result['defect_count']} "
        f"testcases={result['testcase_count']} errors={result['error_count']} "
        f"gate={result['gate']} warnings={result['quality_warning_count']} "
        f"semantic_warnings={result['semantic_warning_count']} "
        f"admissible_warnings={result['admissible_warning_count']} "
        f"blocking_warnings={result['blocking_warning_count']} "
        f"conflicts={result['conflict_count']} "
        f"warning_rate={result['warning_rate']} report={result['report_path']} "
        f"details={result['validation_details_path']} under {args.knowledge_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
