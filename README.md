# Evidence-First Eval Kit

A small, dependency-free toolkit for checking research answer quality. It is designed for source-grounded explanations, technical investigations, and fictional ability analysis.

It does **not** prove an answer is true. It makes review criteria explicit, validates test-case datasets, and calculates transparent scores from human assessments.

## Contents

- docs/RESEARCH_WORKFLOW.md — reproducible research workflow.
- docs/SCORING_RUBRIC.md — eight-dimension rubric and critical-failure rules.
- schemas/ — JSON Schemas for cases and research claims.
- examples/evaluation_cases.jsonl — starter cases on citations, uncertainty, continuity, and reasoning.
- scripts/validate_jsonl.py — standard-library dataset validator.
- scripts/score_evaluations.py — scoring for human assessment records.
- tests/ — offline unit tests.
- .github/workflows/tests.yml — automated validation and tests.

## Requirements

Python 3.10 or newer. The scripts use only the standard library.

Validate the starter dataset:
python scripts/validate_jsonl.py examples/evaluation_cases.jsonl

Run tests:
python -m unittest discover -s tests -v

## Score human assessments

Create an assessment JSONL file with a case_id, a scores object containing all eight rubric dimensions (integer 0–4), and critical_failures (array). Optional notes explain the assessment. The scoring script calculates a weighted 0–100 score.

Critical failures force FAIL regardless of score. Otherwise, PASS is 85+, REVIEW is 70–84.99, and FAIL is below 70. These thresholds are workflow defaults, not scientifically validated cutoffs. Inspect the underlying evidence rather than trusting a score alone.

## Data hygiene

Never commit passwords, API keys, session tokens, private contact details, or confidential source material. Keep user-specific research private; publish only intentionally public material. Pin source versions and dates when facts can change.

## License

MIT. See LICENSE.
