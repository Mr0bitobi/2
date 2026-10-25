from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

validator = load_module("validator", ROOT / "scripts" / "validate_jsonl.py")
scorer = load_module("scorer", ROOT / "scripts" / "score_evaluations.py")

class ValidatorTests(unittest.TestCase):
    def test_example_dataset_validates(self):
        self.assertEqual(validator.validate(ROOT / "examples" / "evaluation_cases.jsonl"), [])

    def test_duplicate_id_is_rejected(self):
        row = {"case_id":"X-1","category":"test","question":"Q?","expected_behavior":["A"],"failure_modes":[]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.jsonl"
            path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
            errors = validator.validate(path)
        self.assertTrue(any("duplicate case_id" in error for error in errors))

class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.scores = {key: 4 for key in scorer.WEIGHTS}

    def test_perfect_score_passes(self):
        result = scorer.score_record({"case_id":"X","scores":self.scores,"critical_failures":[],"notes":""})
        self.assertEqual(result["score_percent"], 100.0)
        self.assertEqual(result["status"], "PASS")

    def test_critical_failure_overrides_perfect_score(self):
        result = scorer.score_record({"case_id":"X","scores":self.scores,"critical_failures":["fabricated_citation"],"notes":""})
        self.assertEqual(result["status"], "FAIL")

    def test_low_score_fails(self):
        low = {key: 1 for key in scorer.WEIGHTS}
        result = scorer.score_record({"case_id":"X","scores":low,"critical_failures":[],"notes":""})
        self.assertEqual(result["status"], "FAIL")

if __name__ == "__main__":
    unittest.main()
