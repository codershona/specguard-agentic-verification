# Improvement Changelog

## Baseline — Case 01

### Approach
A deliberately simple implementation relies only on the repository's existing tests.

The implementation checks the minimum username length but does not systematically verify the full written requirement.

### Evidence

Existing repository tests:

- Passed: 2/2
- Pass rate: 100%

Independent requirement evaluator:

- Passed: 3/10
- Failed: 7/10
- Requirement satisfaction rate: 30%

### Observed failure modes

The implementation failed to enforce:

- Maximum username length
- Leading underscore restriction
- Trailing underscore restriction
- Consecutive underscore restriction
- Allowed-character restrictions
- Space rejection
- Non-ASCII character rejection

### Decision / Learning

Passing the repository's existing tests created false confidence.

The next iteration should derive verification directly from the written requirement rather than assuming that existing tests represent the complete specification.


## Iteration 1 — Structured Requirement Extraction

### What we tried

Added deterministic parsing and initial requirement decomposition.

The workflow converts numbered statements in a requirement document into structured requirements and acceptance criteria.

### Evidence

- Requirement parser extracted: 6/6 numbered requirements
- Parser unit tests: passed
- Decomposer unit tests: passed

### Limitation discovered

The decomposition is syntactic rather than semantic.

For example:

`Not begin or end with an underscore.`

is currently represented as one acceptance criterion even though it contains two independently verifiable behaviors:

- username must not begin with `_`
- username must not end with `_`

### Decision / Learning

Keep deterministic parsing as reliable infrastructure, but introduce an agent for semantic decomposition into truly atomic and testable acceptance criteria.



## Iteration 2 - Semantic Requirement Decomposition

### Goal
Improve requirement decomposition using a local reasoning agent.

### Changes
- Added Ollama integration using `qwen3:4b`.
- Added semantic requirement decomposition.
- Added JSON-constrained model output.
- Added validation and retry handling for malformed model responses.
- Changed decomposition to process each requirement independently.
- Assigned requirement numbers deterministically in Python to preserve traceability.
- Added semantic decomposer unit test using a deterministic fake LLM.

### Failures observed
- Model initially returned reasoning text mixed with JSON.
- Model returned malformed JSON fields.
- Model generated an invalid requirement number.
- Model over-decomposed numeric ranges.
- Model duplicated requirements.
- Requirement 3 was initially not split into independently testable start/end conditions.

### Result
Requirement 3 is now decomposed into:
- Username must not begin with an underscore.
- Username must not end with an underscore.

All unit tests pass: 3/3.


## Iteration 3 - Verification Agent, Probe Critic, and Execution-Grounded Verdicts

### Goal

Verify atomic acceptance criteria against implementation code using generated probes, deterministic validation, and executable evidence.

### Changes

- Added a Verification Agent that generates multiple probes for each acceptance criterion.
- Added structured JSON validation for verifier responses.
- Added retry feedback when model output is malformed or incomplete.
- Added a deterministic probe critic to reject probes that do not directly test the target criterion.
- Added deterministic repair for mandatory boundary and adversarial probes.
- Added execution of generated probes directly against the target implementation.
- Added `confirmed_violation` based on actual probe mismatches.
- Added `final_verdict`, where executable evidence overrides the agent's self-reported verdict.
- Added unit tests for verifier and execution behavior.
- Added trajectory evidence files for initial verification, execution evidence, targeted probes, repaired probes, and final verdict behavior.

### Failures observed

- The agent initially generated probes that did not isolate the acceptance criterion.
- Numeric boundary verification missed the 20/21 character upper boundary.
- Allowed-character verification initially omitted a forbidden-character probe.
- Trailing underscore verification generated incorrect or weak examples.
- Consecutive underscore verification initially failed to test a value containing `__`.
- The model sometimes omitted the required `expected` field.
- The agent repeatedly reported `SATISFIED` even when executable probes demonstrated a requirement violation.

### Improvements

The deterministic critic now guarantees important probes such as:

- length 20 -> `VALID`
- length 21 -> `INVALID_USERNAME`
- `abc!` -> `INVALID_USERNAME`
- `_abc` -> `INVALID_USERNAME`
- `abc_` -> `INVALID_USERNAME`
- `a__b` -> `INVALID_USERNAME`

Execution evidence identified confirmed violations for:

- AC-01: maximum username length
- AC-02: allowed-character restriction
- AC-03: leading underscore restriction
- AC-04: trailing underscore restriction
- AC-05: consecutive underscore restriction

No violation was confirmed by the current probes for:

- AC-06
- AC-07

### Result

All current unit tests pass: 5/5.

The final verification layer now produces execution-grounded verdicts.

For AC-01 through AC-05, the reasoning agent reported:

`SATISFIED`

but executable evidence produced:

`VIOLATED`

For AC-06 and AC-07, all generated probes matched the implementation and the final verdict remained:

`SATISFIED`

### Decision / Learning

LLM reasoning should guide verification, but it should not be treated as the final source of truth.

Generated probes must be validated, repaired where necessary, and executed against the implementation.

SpecGuard therefore uses a hybrid approach:

`Requirement -> Semantic Agent -> Verification Agent -> Deterministic Probe Critic -> Execution -> Final Verdict`

The final verdict is derived from executable evidence rather than blindly trusting the model's self-reported assessment.


## Iteration 4 - Independent Evaluation and Defect Recall

### Goal

Measure SpecGuard against an independent evaluator without exposing
the evaluator tests to the verification agent.

### Evaluation Method

The independent evaluator contains 10 behavioral checks.

The baseline implementation passed 3/10 checks, giving a requirement
satisfaction rate of 30%.

The remaining 7 evaluator failures were mapped to the atomic acceptance
criteria produced by SpecGuard only after verification was completed.

### Results

- Acceptance criteria analyzed: 7
- Criteria classified as violated: 5
- Criteria classified as satisfied: 2
- Criterion violation rate: 71.4%
- Independent evaluator failures: 7
- Evaluator failures detected by SpecGuard: 7/7
- Defect recall: 100.0%

### Key Finding

SpecGuard detected every defect exposed by the independent evaluator
for Case 01.

The 100% result represents defect recall, not implementation correctness.
The target implementation itself remains at 30% evaluator pass rate.

### Decision / Learning

Independent evaluation confirms that execution-grounded verification can
identify requirement violations that are missed by the repository's
existing developer tests.

The next step is to evaluate SpecGuard across additional cases to determine
whether this performance generalizes beyond Case 01.




cat >> CHANGELOG.md <<'EOF'

## Iteration 5 — Email Probe Generalization

### Goal

Extend verification beyond username validation and improve probe generation for email requirements.

### Changes

- Added email-specific probe generation.
- Improved invalid-input handling.
- Added Case 03 evaluation.
- Captured final execution evidence.

### Result

Case 03 was evaluated against an independent evaluator and SpecGuard detected the requirement defects exposed by the benchmark.

---

## Iteration 6 — Typed Input Verification

### Goal

Verify requirements involving input types rather than only string values.

### Changes

- Added typed probe generation.
- Added Case 04 evaluation.
- Added verification of invalid input types.
- Preserved executable evidence for each probe.

### Result

Case 04 was successfully evaluated and requirement defects were detected through execution-grounded verification.

---

## Iteration 7 — Multi-Argument Verification

### Goal

Support requirements where behavior depends on multiple function arguments.

### Changes

- Added structured multi-argument probe inputs.
- Extended execution to pass dictionary-based arguments to target functions.
- Added Case 05 evaluation.
- Added evidence for multi-argument verification.

### Result

SpecGuard successfully verified multi-argument requirements and identified missing behaviors in the implementation.

---

## Iteration 8 — Numeric Probe Generalization

### Goal

Improve verification of numeric boundaries and range-based requirements.

### Changes

- Generalized numeric probe generation.
- Added boundary-oriented probes.
- Added Case 06 evaluation.
- Preserved execution evidence for numeric requirements.

### Result

Case 06 demonstrated that generated probes can expose requirement gaps beyond the repository's developer tests.

---

## Iteration 9 — Availability Outcomes

### Goal

Support requirements whose expected outcomes use availability-specific result values.

### Changes

- Added support for `AVAILABLE`.
- Added support for `UNAVAILABLE`.
- Updated verification-response validation.
- Added Case 07 evaluation.

### Result

The verification pipeline successfully handled availability-specific outcomes and detected the missing requirement behaviors in Case 07.

---

## Iteration 10 — Transfer Verification

### Goal

Generalize verification for transaction and transfer-style requirements.

### Changes

- Added transfer-specific probe generation.
- Added multi-argument transfer probes.
- Added support for approval and invalid-transfer outcomes.
- Added Case 08 evaluation.
- Added final execution evidence.

### Result

Case 08 exposed requirement gaps involving amount/balance relationships and invalid input types.

---

## Iteration 11 — Coupon Verification

### Goal

Extend verification to structured coupon validation requirements.

### Changes

- Added coupon-specific probe generation.
- Added support for coupon validity outcomes.
- Generalized expected-result validation.
- Added Case 09 evaluation.
- Added final execution evidence.

### Result

Case 09 demonstrated that executable probes could expose missing constraints involving coupon format, case sensitivity, prefix requirements, and related validation behavior.

---

## Iteration 12 — Transaction Verification and Case 10

### Goal

Generalize transaction-style verification for withdrawal requirements.

### Changes

- Added withdrawal-specific verification behavior.
- Generalized invalid-result handling.
- Added multi-argument withdrawal probes.
- Added Case 10 evaluation.
- Added final execution evidence.

### Result

Case 10 exposed implementation gaps involving withdrawal limits, balance constraints, and boolean input handling.

---

## Iteration 13 — Execution Error Handling

### Goal

Prevent execution failures from being incorrectly classified as requirement violations or successful verification.

### Changes

- Added explicit detection of successful probe executions.
- Added `inconclusive` final verdict handling.
- Execution errors no longer count as confirmed requirement violations.
- Added a regression test for all-error execution scenarios.
- Added execution-error evidence.
- Added aggregate evaluation metrics.

### Result

The execution layer now distinguishes three states:

- `violated` — executable evidence confirms a mismatch.
- `satisfied` — executable evidence provides successful verification.
- `inconclusive` — execution failed to provide usable evidence.

The project test suite passes all six tests.

### Decision / Learning

Execution errors are evidence that verification could not be completed, not evidence that the requirement itself was violated.

This makes the final verdict more conservative and evidence-driven.
EOF