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