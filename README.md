# SpecGuard Agentic Verification

Evidence-driven agentic workflow for verifying software changes against written requirements.

## Overview

SpecGuard verifies whether an implementation satisfies the behavior described in a requirement document.

Instead of relying only on developer-written tests, SpecGuard derives verification criteria from the written specification, generates executable probes, validates those probes deterministically, executes them against the implementation, and uses the resulting evidence to produce the final verdict.

The core workflow is:

Requirement
→ Requirement Parser
→ Semantic Decomposer
→ Verification Agent
→ Deterministic Probe Critic / Repair
→ Probe Execution
→ Evidence
→ Final Verdict

## Why SpecGuard?

Passing existing developer tests does not necessarily mean that an implementation satisfies the complete written requirement.

In the baseline Case 01 evaluation:

- Developer tests passed: 2/2
- Independent evaluator passed: 3/10
- Independent evaluator failures: 7

SpecGuard identified all 7 requirement defects exposed by the independent evaluator.

This demonstrates the central principle of the project:

> Passing developer tests is not sufficient evidence of full requirement satisfaction.

## Architecture

### 1. Requirement Parsing

The requirement document is parsed into structured numbered requirements.

### 2. Semantic Decomposition

A local reasoning agent decomposes requirements into atomic acceptance criteria that can be independently verified.

### 3. Verification Agent

The verification agent analyzes the implementation and acceptance criterion and generates multiple executable probes.

### 4. Deterministic Probe Validation

Generated probes are checked to ensure that they actually test the target acceptance criterion.

Important boundary and adversarial probes can be repaired or added deterministically.

### 5. Execution

Validated probes are executed directly against the target implementation.

Each probe records:

- input
- expected result
- actual result
- whether the result matched
- execution error, if any

### 6. Final Verdict

The final verdict is based on executable evidence rather than blindly trusting the verification agent's self-reported verdict.

Possible final outcomes are:

- `satisfied` — executable probes provide successful evidence.
- `violated` — at least one executable probe produces a confirmed mismatch.
- `inconclusive` — probes cannot provide usable execution evidence because all executions fail.

This distinction prevents execution errors from being incorrectly interpreted as requirement violations or successful verification.

## Evaluation

SpecGuard was evaluated across 10 independent requirement-validation cases.

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

Across the 10 cases:

- Independent evaluator tests: 97
- Baseline tests passed: 64
- Baseline pass rate: 66.0%
- Unique requirement defects: 26
- Defects detected by SpecGuard: 26
- Unique-defect recall: 100%

The aggregate evaluation is documented in:

`evaluation/results/aggregate_metrics.md`

## Evidence and Trajectories

The `trajectories/` directory records the development and verification process.

Evidence includes:

- initial verification
- generated probes
- targeted probes
- repaired probes
- execution results
- final verdicts
- case-specific evaluation evidence
- execution-error handling evidence

This provides an auditable trail showing how verification decisions were reached.

## Evaluation Cases

The benchmark contains 10 independent cases:

1. Username validation
2. Password validation
3. Email validation
4. Quantity validation
5. Date range validation
6. Discount validation
7. Username availability
8. Transfer validation
9. Coupon validation
10. Withdrawal validation

Each case contains:

- `requirement.md` — written specification
- `app.py` — target implementation
- `test_app.py` — developer tests
- `evaluator_test.py` — independent evaluator

## Project Structure

```text
specguard-agentic-verification/
├── specguard/
│   ├── parser.py
│   ├── decomposer.py
│   ├── semantic_decomposer.py
│   ├── verifier.py
│   ├── execution.py
│   ├── llm.py
│   └── models.py
│
├── tests/
│   ├── test_parser.py
│   ├── test_decomposer.py
│   ├── test_semantic_decomposer.py
│   ├── test_verifier.py
│   └── test_execution.py
│
├── evaluation/
│   ├── cases/
│   │   ├── case_01/
│   │   ├── case_02/
│   │   ├── ...
│   │   └── case_10/
│   └── results/
│
├── trajectories/
├── baseline/
├── docs/
├── CHANGELOG.md
├── requirements.txt
└── README.md
