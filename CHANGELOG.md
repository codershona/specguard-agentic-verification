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