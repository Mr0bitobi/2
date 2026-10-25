# Answer Quality Scoring Rubric

Score each dimension from 0 to 4. Scores help locate review work; they are not proof of factual correctness.

| Dimension | What to check |
|---|---|
| factual_accuracy | Do claims match the best available evidence? Are facts and interpretations separated? |
| source_quality | Are sources relevant, authoritative for the question, and traceable to the original? |
| citation_coverage | Can a reader trace each material claim to evidence that actually supports it? |
| reasoning | Are assumptions explicit and inference steps valid? Are alternatives considered? |
| uncertainty_calibration | Does confidence match the evidence? Are unknowns and disagreements visible? |
| completeness | Does the answer address the question, relevant limitations, and important exceptions? |
| counterexample_testing | Were plausible counterexamples and disconfirming evidence checked? |
| instruction_fit | Does the answer respect the requested scope, format, and constraints? |

## Anchors

- 0 — absent/failed: fundamentally unsupported or ignored.
- 1 — weak: major gaps; substantial correction required.
- 2 — partial: useful work exists, but meaningful gaps remain.
- 3 — strong: only minor, identified gaps remain.
- 4 — very strong: careful, traceable, and fit for the stated purpose.

## Default weights

| Dimension | Weight |
|---|---:|
| Factual accuracy | 2.0 |
| Source quality | 1.5 |
| Citation coverage | 1.5 |
| Reasoning | 1.5 |
| Uncertainty calibration | 1.0 |
| Completeness | 1.0 |
| Counterexample testing | 1.0 |
| Instruction fit | 0.5 |

The weighted score is converted to 0–100. Default statuses: PASS at 85 or above; REVIEW from 70 to below 85; FAIL below 70. These are operational defaults, not validated psychometric cutoffs.

## Critical failures

A critical failure overrides the numeric score and forces FAIL. Example labels:

- fabricated_citation
- source_does_not_support_claim
- serious_factual_error
- unsupported_high_impact_claim
- privacy_leak
- safety_failure
- continuity_conflation
- no_limits_fallacy

Use a critical label only when a reviewer can explain the concrete defect. Record that explanation in notes.

## Review loop

1. Score from the evidence record where feasible.
2. Name the two weakest dimensions and the evidence behind them.
3. Correct the answer and re-check citations.
4. Re-score the revised version; retain both records for comparisons.
5. Inspect recurring failure categories, not just averages.
