# SpecGuard Agent Trajectories

This document provides representative end-to-end trajectories for every LLM-based agent used by SpecGuard.

The raw evidence referenced below is preserved in the `trajectories/` directory.

## 1. Agents Used

SpecGuard uses two LLM-based agent roles:

1. **Semantic Decomposer Agent**
   - Model: local Ollama `qwen3:4b`
   - Purpose: transform written requirements into independently verifiable acceptance criteria.

2. **Verification Agent**
   - Model: local Ollama `qwen3:4b`
   - Purpose: reason about an acceptance criterion and target implementation and propose verification probes.

The agents do not have final authority over requirement correctness. Deterministic validation, probe repair, and executable evidence are used to validate their outputs.

## 2. Semantic Decomposer Agent Trajectory

### Goal

Convert natural-language requirements into small, independently verifiable acceptance criteria.

### Agent Action

The semantic agent processes requirements independently and returns JSON-constrained decompositions.

Requirement numbering is assigned deterministically in Python rather than trusted to the model.

### Observed Agent Failures

During Iteration 02, the model:

- mixed reasoning text with JSON
- returned malformed JSON fields
- generated invalid requirement numbers
- over-decomposed numeric ranges
- duplicated requirements
- initially failed to split Requirement 3 correctly

### Feedback and Retry

SpecGuard added deterministic output validation and retry handling around the semantic agent.

The model remained responsible for semantic reasoning, while Python code validated the structure and numbering of its output.

### Final Result

Requirement 3 was correctly decomposed into two independent criteria:

- Username must not begin with an underscore.
- Username must not end with an underscore.

The semantic decomposition test passed, and the project test suite reached 3/3 passing tests at the end of Iteration 02.

### Learning

LLM reasoning improved semantic decomposition, but model output could not be trusted without deterministic validation, retries, and traceability.

### Raw Evidence

See:

`iteration_02_summary.txt`

## 3. Verification Agent Trajectory

### Goal

Evaluate each acceptance criterion against the target implementation and propose concrete verification probes with expected outcomes.

### Initial Agent Action

The Verification Agent reasons about the acceptance criterion and implementation, produces an advisory verdict, explains its reasoning, and proposes test inputs with expected outputs.

During the initial Case 01 verification, the agent generated probes for username length, allowed characters, leading and trailing underscores, consecutive underscores, and return-value behavior.

### Problem Observed

The agent's own verdict and reasoning were not always reliable enough to serve as final verification evidence.

For example, after probe repair the agent reported AC-01 as:

`Agent verdict: SATISFIED`

However, execution of the repaired boundary probe produced:

```text
Input: 'aaaaaaaaaaaaaaaaaaaaa'
Expected: INVALID_USERNAME
Actual: VALID
Matched: False
```

This provided executable evidence that the implementation violated the maximum-length requirement.

Similar execution-backed contradictions were observed for AC-02 through AC-05.

### Deterministic Feedback and Repair

Agent-generated probes are not executed blindly.

SpecGuard validates and, when necessary, repairs probes to improve:

- requirement alignment
- boundary coverage
- valid and invalid input coverage
- expected-output consistency
- probe isolation
- input structure

The repaired probes are then executed against the target implementation.

### Tool / Execution Response

For Case 01, execution produced mismatches for five acceptance criteria:

- AC-01 — maximum username length
- AC-02 — allowed characters
- AC-03 — leading underscore
- AC-04 — trailing underscore
- AC-05 — consecutive underscores

AC-06 and AC-07 had no confirmed executable mismatch in the generated evidence.

### Final Evidence-Grounded Verdict

Execution evidence overrides the advisory agent verdict.

The resulting Case 01 verdicts were:

```text
AC-01: Agent SATISFIED -> Final VIOLATED
AC-02: Agent SATISFIED -> Final VIOLATED
AC-03: Agent SATISFIED -> Final VIOLATED
AC-04: Agent SATISFIED -> Final VIOLATED
AC-05: Agent SATISFIED -> Final VIOLATED
AC-06: Agent SATISFIED -> Final SATISFIED
AC-07: Agent SATISFIED -> Final SATISFIED
```

This demonstrates that the LLM is used to propose useful verification actions, while executable evidence determines the final requirement verdict.

### Raw Evidence

See:

- `iteration_03_initial_verification.txt`
- `iteration_03_repaired_probe_evidence.txt`
- `iteration_03_execution_evidence.txt`
- `iteration_03_final_verdict_evidence.txt`

## 4. Evaluation Boundary and Human Checkpoints

### Independent Evaluation Boundary

The independent evaluator tests are kept outside the agents' verification context.

Neither the Semantic Decomposer Agent nor the Verification Agent receives the hidden evaluator cases as guidance when generating acceptance criteria or verification probes.

This separation prevents the verification workflow from simply optimizing against evaluator examples.

### Human Checkpoint

SpecGuard operates on local benchmark implementations and does not perform consequential external actions, so human approval is not required before probe execution.

Human review is instead supported through auditable artifacts:

- acceptance criteria
- agent reasoning
- generated probes
- deterministic repairs
- expected and actual outputs
- execution matches and mismatches
- final verdicts
- development trajectories
- independent evaluator results

This allows a reviewer to inspect how a final verdict was reached without treating the LLM response itself as authoritative.

## 5. End-to-End Agent Trajectory Summary

The complete verification path is:

```text
Written Requirement
        |
        v
Semantic Decomposer Agent
        |
        v
Deterministic Output Validation
        |
        +---- invalid output ----> retry / validation feedback
        |
        v
Acceptance Criteria
        |
        v
Verification Agent
        |
        v
Generated Verification Probes
        |
        v
Deterministic Validation / Repair
        |
        v
Probe Execution Against Implementation
        |
        v
Expected vs Actual Evidence
        |
        v
Execution-Grounded Final Verdict

## 6. Additional Development Trajectories

Further trajectories show how the workflow evolved across the benchmark, including:

- email-validation generalization failure
- typed JSON primitive handling
- multi-argument verification
- numeric boundary generalization
- availability-style outcomes
- transaction constraints
- coupon expected-output generalization
- execution-error handling

See `README.md` in this directory for the complete Iteration 01–13 trace index.
