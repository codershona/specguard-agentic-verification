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





## Iteration 5 — Email Probe Generalization

### Goal

Test whether verification behavior generalized from username/password requirements to a different validation domain.

### What we tried

Extended probe generation and deterministic repair for email-validation requirements.

### Failure observed

Password-oriented repair behavior leaked into the email case, demonstrating that case-specific repair logic could generate irrelevant probes when applied too broadly.

### Evidence

Case 03 baseline:

- Developer tests: 2/2 passed
- Independent evaluator: 6/9 passed (66.7%)
- Unique requirement defects: 3

The missing behaviors covered:

- domain-dot validation
- space rejection
- non-ASCII rejection

After repairing the generalization problem, SpecGuard detected all 3 unique defects.

Evidence:

`trajectories/iteration_05_case_03_generalization_failure.txt`

`trajectories/iteration_05_case_03_final_evidence.txt`

### Decision / Learning

Unscoped case-specific repair heuristics do not generalize safely.

Repair behavior should be constrained by the current requirement semantics rather than inherited from an unrelated validation domain.

This experiment led to removing the leaking password-oriented behavior from the email verification path and replacing it with requirement-appropriate repair logic.

---

## Iteration 6 — Typed Input Verification

### Goal

Extend verification beyond string-only inputs.

### What we tried

Preserved JSON primitive types in generated probes and added typed-input verification for quantity requirements.

### Failure observed

Early response handling treated values such as `0` and `False` as missing because they are falsey in Python.

This prevented valid typed probes from being represented correctly.

### Evidence

Case 04 baseline:

- Developer tests: 2/2 passed
- Independent evaluator: 7/9 passed (77.8%)
- Unique requirement defects: 2

Missing behaviors:

- values above the maximum boundary
- boolean-input rejection

After typed-input handling was corrected, SpecGuard detected both unique defects.

Evidence:

`trajectories/iteration_06_case_04_typed_input_failure.txt`

`trajectories/iteration_06_case_04_final_evidence.txt`

### Decision / Learning

Probe validation must preserve the distinction between a missing value and a valid falsey primitive.

Agent-generated structured data requires deterministic schema handling before execution.

---

## Iteration 7 — Multi-Argument Verification

### Goal

Support requirements whose behavior depends on multiple function arguments.

### What we tried

Added dictionary-based probe inputs and execution through keyword arguments.

### Failure observed

Initial multi-argument verification was incomplete because the existing execution path was designed primarily around single-input functions.

### Evidence

Case 05 baseline:

- Developer tests: 2/2 passed
- Independent evaluator: 8/10 passed (80.0%)
- Unique requirement defects: 2

Missing behaviors:

- end date above the allowed maximum
- boolean-input rejection

After multi-argument support was added, SpecGuard detected both unique defects.

Evidence:

`trajectories/iteration_07_case_05_partial_multi_argument_evidence.txt`

`trajectories/iteration_07_case_05_final_evidence.txt`

### Decision / Learning

Executable verification needs to model the target function's invocation structure, not only the semantic requirement.

Multi-argument requirements therefore require structured probes that preserve all required parameters.

---

## Iteration 8 — Numeric Probe Generalization

### Goal

Improve reusable verification of numeric boundaries and invalid numeric types.

### What we tried

Generalized numeric probe generation and boundary-oriented deterministic repairs.

### Evidence

Case 06 baseline:

- Developer tests: 2/2 passed
- Independent evaluator: 7/10 passed (70.0%)
- Unique requirement defects: 2

Missing behaviors:

- discount above the maximum value
- boolean-input rejection

SpecGuard detected both unique defect dimensions.

Evidence:

`trajectories/iteration_08_case_06_final_evidence.txt`

### Decision / Learning

Numeric verification benefits from deterministic boundary probes around requirement thresholds.

The strongest workflow combines agent interpretation of the requirement with deterministic generation of high-value boundary evidence.

---

## Iteration 9 — Availability Outcomes

### Goal

Generalize expected-result handling beyond `VALID` and `INVALID_*` responses.

### What we tried

Added support for domain-specific outcomes including `AVAILABLE` and `UNAVAILABLE`.

### Evidence

Case 07 baseline:

- Developer tests: 2/2 passed
- Independent evaluator: 7/10 passed (70.0%)
- Unique requirement defects: 2

Missing behaviors:

- maximum username length
- case-insensitive comparison against taken usernames

SpecGuard detected both unique defect dimensions.

Evidence:

`trajectories/iteration_09_case_07_final_evidence.txt`

### Decision / Learning

A verification framework cannot assume that all specifications use generic valid/invalid result labels.

Expected-result validation must accommodate the vocabulary defined by the target specification.

---

## Iteration 10 — Transfer Verification

### Goal

Stress-test multi-argument verification using transaction relationships.

### What we tried

Extended transaction-oriented probes for amount and balance relationships.

### Failure observed

Some generated probes supplied only one argument to a multi-argument function.

Those probes produced execution errors and revealed that execution failure could be confused with evidence of a requirement violation.

### Evidence

Case 08 baseline:

- Developer tests: 2/2 passed
- Independent evaluator: 7/10 passed (70.0%)
- Unique requirement defects: 2

Missing behaviors:

- amount exceeding balance
- boolean-input rejection

After strengthening multi-argument probes and execution handling, SpecGuard detected both unique defect dimensions.

Evidence:

`trajectories/iteration_10_case_08_final_evidence.txt`

### Decision / Learning

An execution error is not evidence that an implementation violates a requirement.

Only successfully executed probes that produce mismatched behavior should confirm a violation.

This failure directly motivated the more conservative execution semantics finalized in Iteration 13.

---

## Iteration 11 — Coupon Verification

### Goal

Test verification against structured string constraints with domain-specific success values.

### What we tried

Extended probe generation for length, character-set, case-sensitivity, and prefix requirements.

### Failure observed

The verifier initially generated the generic expected result `VALID`, while the specification required `VALID_COUPON`.

Expected-result validation was therefore generalized without treating the agent's original label as authoritative.

### Evidence

Case 09 baseline:

- Developer tests: 2/2 passed
- Independent evaluator: 6/10 passed (60.0%)
- Unique requirement defects: 2

Missing defect dimensions:

- uppercase ASCII requirement
- required `SAVE` prefix

SpecGuard detected both unique defect dimensions.

Evidence:

`trajectories/iteration_11_case_09_final_evidence.txt`

### Decision / Learning

Agent-generated expected labels need deterministic validation against the specification's output vocabulary.

Semantic correctness matters more than accepting the model's first textual representation.

---

## Iteration 12 — Withdrawal Verification

### Goal

Verify that transaction-oriented logic generalized from transfer requirements to withdrawal requirements.

### What we tried

Generalized transaction verification, invalid-result handling, and multi-argument withdrawal probes.

### Evidence

Case 10 baseline:

- Developer tests: 2/2 passed
- Independent evaluator: 8/10 passed (80.0%)
- Unique requirement defects: 2

Missing behaviors:

- amount exceeding available balance
- boolean balance handling

SpecGuard detected both unique defect dimensions.

Evidence:

`trajectories/iteration_12_case_10_final_evidence.txt`

### Decision / Learning

Transaction verification could be reused across related domains once expected-result handling and multi-argument execution were separated from case-specific result names.

---

## Iteration 13 — Execution Error Handling and Final Evaluation

### Goal

Prevent execution failures from being incorrectly classified as requirement violations or successful verification.

### What we tried

Changed final-verdict calculation to distinguish executable mismatches from probe execution failures.

### Changes

- Execution errors no longer count as confirmed violations.
- Added detection of whether any probe executed successfully.
- Added an explicit `inconclusive` verdict when all probes fail to execute.
- Added a regression test for the all-error scenario.
- Re-ran the complete benchmark.

### Evidence

A deliberately invalid invocation produced a `TypeError`.

Rather than reporting `violated`, SpecGuard now reports:

`inconclusive`

with:

`confirmed_violation = False`

Evidence:

`trajectories/iteration_13_execution_inconclusive_evidence.txt`

Final aggregate benchmark:

- Evaluation cases: 10
- Independent evaluator tests: 97
- Baseline evaluator tests passed: 64/97 (66.0%)
- Failing evaluator scenarios: 33
- Unique requirement defects: 26
- Unique defects detected by SpecGuard: 26/26
- Primary metric — unique-defect recall: 100%
- Core project tests: 6/6 passed

Aggregate evidence:

`evaluation/results/aggregate_metrics.md`

### Decision / Learning

Execution errors mean that verification could not establish usable evidence; they do not prove either satisfaction or violation.

The final system therefore uses three evidence-grounded outcomes:

- `satisfied`
- `violated`
- `inconclusive`

## Main Failure Mode and Hot Take

### Main Failure Mode

The most important recurring failure mode was trusting agent-generated probes or labels before verifying that they were semantically aligned, structurally valid, and executable.

Examples included case-specific repair leakage, falsey typed inputs, incomplete multi-argument probes, and incorrect expected-result labels.

These failures led to the hybrid architecture used in the final system: agent reasoning proposes verification actions, while deterministic validation, repair, and execution determine whether those actions provide usable evidence.

### Hot Take

**The most reliable role for an agent in software verification is not to declare whether the code is correct. It is to propose high-value tests whose claims can be checked independently.**

SpecGuard improved when the agent became less authoritative: semantic reasoning remained useful for generating verification probes, but deterministic validation and executable evidence became the source of truth.
