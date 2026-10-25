#!/usr/bin/env python3
"""Calculate transparent summary scores for human-reviewed answer evaluations."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any

WEIGHTS = {
    "factual_accuracy": 2.0,
    "source_quality": 1.5,
    "citation_coverage": 1.5,
    "reasoning": 1.5,
    "uncertainty_calibration": 1.0,
    "completeness": 1.0,
    "counterexample_testing": 1.0,
    "instruction_fit": 0.5,
}
CRITICAL_FAILURES = {
    "fabricated_citation", "source_does_not_support_claim", "serious_factual_error",
    "unsupported_high_impact_claim", "privacy_leak", "safety_failure",
    "continuity_conflation", "no_limits_fallacy",
}


def read_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_no}: invalid JSON: {exc.msg}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"line {line_no}: expected a JSON object")
        case_id = item.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"line {line_no}: case_id must be a non-empty string")
        scores = item.get("scores")
        if not isinstance(scores, dict):
            raise ValueError(f"line {line_no} ({case_id}): scores must be an object")
        missing = sorted(set(WEIGHTS) - scores.keys())
        extra = sorted(scores.keys() - set(WEIGHTS))
        if missing or extra:
            raise ValueError(f"line {line_no} ({case_id}): score keys missing={missing}, unknown={extra}")
        for name, value in scores.items():
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 4:
                raise ValueError(f"line {line_no} ({case_id}): {name} must be an integer from 0 to 4")
        failures = item.get("critical_failures", [])
        if not isinstance(failures, list) or any(not isinstance(f, str) or not f.strip() for f in failures):
            raise ValueError(f"line {line_no} ({case_id}): critical_failures must be an array of non-empty strings")
        notes = item.get("notes", "")
        if not isinstance(notes, str):
            raise ValueError(f"line {line_no} ({case_id}): notes must be a string")
        records.append({"case_id": case_id, "scores": scores, "critical_failures": failures, "notes": notes})
    if not records:
        raise ValueError("input contains no evaluation records")
    return records


def score_record(record: dict[str, Any]) -> dict[str, Any]:
    weight_sum = sum(WEIGHTS.values())
    weighted_points = sum(record["scores"][name] * weight for name, weight in WEIGHTS.items())
    percentage = round(weighted_points / (4 * weight_sum) * 100, 2)
    failures = record["critical_failures"]
    if failures:
        status = "FAIL"
    elif percentage >= 85:
        status = "PASS"
    elif percentage >= 70:
        status = "REVIEW"
    else:
        status = "FAIL"
    ranked = sorted(WEIGHTS, key=lambda key: (record["scores"][key] / 4, -WEIGHTS[key]))
    return {
        "case_id": record["case_id"], "score_percent": percentage, "status": status,
        "critical_failures": failures, "weakest_dimensions": ranked[:2], "notes": record["notes"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="JSONL file of human evaluation records")
    args = parser.parse_args()
    try:
        records = read_records(args.path)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    results = [score_record(record) for record in records]
    output = {
        "records_scored": len(results),
        "average_score_percent": round(sum(r["score_percent"] for r in results) / len(results), 2),
        "status_counts": {status: sum(r["status"] == status for r in results) for status in ("PASS", "REVIEW", "FAIL")},
        "results": results,
        "warning": "Scores are human-review aids, not proof of truth; critical failures override the numeric score.",
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
