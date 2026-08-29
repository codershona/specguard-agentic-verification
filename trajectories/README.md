# SpecGuard Development & Verification Traces

This directory contains the development and verification traces produced while building and evaluating SpecGuard.

The traces document how the system evolved from an initial deterministic requirement parser into an execution-grounded agentic verification workflow.

They provide an auditable record of:

- baseline verification gaps
- semantic requirement decomposition
- agent-generated verification probes
- deterministic probe validation and repair
- execution-backed evidence
- failures discovered during generalization
- improvements made across evaluation cases
- final execution verdicts
- inconclusive execution handling

## Trace Evolution

### Iterations 1–3 — Core Verification Pipeline

These traces capture the initial construction of the SpecGuard workflow.

Key evidence:

- `iteration_01_summary.txt`
- `iteration_02_summary.txt`
- `iteration_03_initial_verification.txt`
- `iteration_03_targeted_probe_evidence.txt`
- `iteration_03_repaired_probe_evidence.txt`
- `iteration_03_execution_evidence.txt`
- `iteration_03_final_verdict_evidence.txt`

The system evolved from deterministic parsing and decomposition to semantic decomposition, agent-generated probes, deterministic repair, execution, and evidence-grounded verdicts.

### Iteration 4 — Baseline Evaluation and Password Generalization

Key evidence:

- `iteration_04_case_01_evaluation.txt`
- `iteration_04_case_02_initial_evidence.txt`
- `iteration_04_case_02_isolation_v2_evidence.txt`
- `iteration_04_case_02_final_evidence.txt`
- `iteration_04_scoring_summary.txt`

This iteration demonstrated that passing developer tests did not guarantee complete requirement satisfaction and expanded verification beyond the original username-validation case.

### Iteration 5 — Email Validation

Key evidence:

- `iteration_05_case_03_generalization_failure.txt`
- `iteration_05_case_03_final_evidence.txt`

A generalization failure exposed case-specific probe-repair behavior. The verifier was improved and successfully detected the intended email-validation defects.

### Iteration 6 — Typed Inputs

Key evidence:

- `iteration_06_case_04_typed_input_failure.txt`
- `iteration_06_case_04_final_evidence.txt`

This iteration exposed limitations in handling non-string JSON primitives and added typed-input verification.

### Iteration 7 — Multi-Argument Verification

Key evidence:

- `iteration_07_case_05_partial_multi_argument_evidence.txt`
- `iteration_07_case_05_final_evidence.txt`

SpecGuard was extended to generate and execute probes for functions requiring multiple named arguments.

### Iteration 8 — Numeric Boundary Generalization

Key evidence:

- `iteration_08_case_06_final_evidence.txt`

Numeric boundary verification and deterministic probe repair were strengthened using the discount-validation case.

### Iteration 9 — Availability Outcomes

Key evidence:

- `iteration_09_case_07_final_evidence.txt`

The verifier was generalized beyond simple VALID/INVALID outcomes to support availability-style results.

### Iteration 10 — Transfer Verification

Key evidence:

- `iteration_10_case_08_final_evidence.txt`

Multi-argument transaction verification was evaluated using transfer validation, including balance constraints and boolean-input handling.

### Iteration 11 — Coupon Verification

Key evidence:

- `iteration_11_case_09_final_evidence.txt`

The system was evaluated against case-sensitive coupon requirements, prefix constraints, and character restrictions.

### Iteration 12 — Withdrawal Verification

Key evidence:

- `iteration_12_case_10_final_evidence.txt`

Transaction verification was further generalized using withdrawal requirements and balance-dependent behavior.

### Iteration 13 — Inconclusive Execution Evidence

Key evidence:

- `iteration_13_execution_inconclusive_evidence.txt`

Execution failures were separated from confirmed requirement violations.

If all probes fail to execute and no usable evidence exists, SpecGuard now returns:

`inconclusive`

rather than incorrectly reporting `satisfied` or `violated`.

## Evaluation Summary

Across the 10-case benchmark:

- Independent evaluator tests: **97**
- Baseline tests passed: **64/97 (66.0%)**
- Failing evaluator scenarios: **33**
- Unique requirement defects: **26**
- Unique defects detected by SpecGuard: **26/26**
- Unique-defect recall: **100%**

The 100% recall result applies specifically to the 26 unique requirement defects represented in this benchmark.

Full aggregate metrics are available at:

`../evaluation/results/aggregate_metrics.md`

## Why These Traces Matter

The traces show not only the final result but also the engineering trajectory used to reach it.

They capture cases where an early verification approach failed to generalize, the evidence that exposed the limitation, and the subsequent improvement to the verification workflow.

This makes the development process reproducible and provides evidence for how SpecGuard's agentic verification capabilities evolved throughout the project.
