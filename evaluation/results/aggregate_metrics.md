# SpecGuard Aggregate Evaluation Results

## Evaluation Summary

SpecGuard was evaluated across 10 independent requirement-validation cases.

The baseline represents conventional developer tests and independent evaluator tests before SpecGuard analysis.

### Baseline Evaluator Results

| Case | Domain | Passed | Total | Pass Rate |
|---|---|---:|---:|---:|
| 01 | Username Validation | 3 | 10 | 30.0% |
| 02 | Password Validation | 5 | 9 | 55.6% |
| 03 | Email Validation | 6 | 9 | 66.7% |
| 04 | Quantity Validation | 7 | 9 | 77.8% |
| 05 | Date Range Validation | 8 | 10 | 80.0% |
| 06 | Discount Validation | 7 | 10 | 70.0% |
| 07 | Username Availability | 7 | 10 | 70.0% |
| 08 | Transfer Validation | 7 | 10 | 70.0% |
| 09 | Coupon Validation | 6 | 10 | 60.0% |
| 10 | Withdrawal Validation | 8 | 10 | 80.0% |
| **Overall** | | **64** | **97** | **66.0%** |

The independent evaluator exposed 33 failing test scenarios that were not covered by the developer tests.

## SpecGuard Defect Detection

Defects are counted by unique missing requirement behavior rather than by duplicate failing probes or semantically decomposed acceptance criteria.

| Case | Unique Requirement Defects | Detected by SpecGuard | Recall |
|---|---:|---:|---:|
| 01 | 5 | 5 | 100% |
| 02 | 4 | 4 | 100% |
| 03 | 3 | 3 | 100% |
| 04 | 2 | 2 | 100% |
| 05 | 2 | 2 | 100% |
| 06 | 2 | 2 | 100% |
| 07 | 2 | 2 | 100% |
| 08 | 2 | 2 | 100% |
| 09 | 2 | 2 | 100% |
| 10 | 2 | 2 | 100% |
| **Overall** | **26** | **26** | **100%** |

## Key Result

Developer tests passed for every evaluation case while the independent evaluator revealed substantial requirement gaps.

Across 97 independent evaluator tests, the baseline implementation passed only 64 tests (66.0%).

SpecGuard detected all 26 unique missing requirement behaviors represented by those failures, achieving 100% unique-defect recall across the 10-case benchmark.

This evaluation demonstrates the value of requirement-driven verification: passing developer tests does not necessarily mean that an implementation satisfies the full specification.
