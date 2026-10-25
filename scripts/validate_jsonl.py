#!/usr/bin/env python3
"""Validate the structural integrity of an evidence-first evaluation JSONL file."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

REQUIRED = {"case_id", "category", "question", "expected_behavior", "failure_modes"}
STRING_FIELDS = ("case_id", "category", "question")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    count = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"Cannot read {path}: {exc}"]

    for line_no, raw in enumerate(lines, 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(item, dict):
            errors.append(f"line {line_no}: each row must be a JSON object")
            continue
        missing = sorted(REQUIRED - item.keys())
        if missing:
            errors.append(f"line {line_no}: missing required fields: {', '.join(missing)}")
        unknown = sorted(item.keys() - (REQUIRED | {"critical", "notes"}))
        if unknown:
            errors.append(f"line {line_no}: unknown fields: {', '.join(unknown)}")
        for key in STRING_FIELDS:
            if key in item and (not isinstance(item[key], str) or not item[key].strip()):
                errors.append(f"line {line_no}: {key} must be a non-empty string")
        for key in ("expected_behavior", "failure_modes"):
            if key in item and (not isinstance(item[key], list) or any(not isinstance(x, str) or not x.strip() for x in item[key])):
                errors.append(f"line {line_no}: {key} must be an array of non-empty strings")
        if isinstance(item.get("expected_behavior"), list) and not item["expected_behavior"]:
            errors.append(f"line {line_no}: expected_behavior must not be empty")
        if "critical" in item and not isinstance(item["critical"], bool):
            errors.append(f"line {line_no}: critical must be a boolean")
        if "notes" in item and not isinstance(item["notes"], str):
            errors.append(f"line {line_no}: notes must be a string")
        case_id = item.get("case_id")
        if isinstance(case_id, str) and case_id.strip():
            if case_id in seen:
                errors.append(f"line {line_no}: duplicate case_id {case_id!r}")
            seen.add(case_id)
        count += 1

    if count == 0:
        errors.append("file contains no test cases")
    if not errors:
        print(f"OK: validated {count} evaluation case(s) in {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="JSONL evaluation case file")
    args = parser.parse_args()
    errors = validate(args.path)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
