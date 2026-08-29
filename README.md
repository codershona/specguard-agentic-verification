# SpecGuard Agentic Verification

Evidence-driven agentic workflow for verifying software changes against written requirements.

## Overview

SpecGuard verifies whether an implementation satisfies the behavior described in a requirement document.

Instead of relying only on developer-written tests, SpecGuard derives verification criteria from the written specification, generates executable probes, validates those probes deterministically, executes them against the implementation, and uses the resulting evidence to produce the final verdict.

The core workflow is:

```text
Requirement
    ↓
Requirement Parser
    ↓
Semantic Decomposer
    ↓
Verification Agent
    ↓
Deterministic Probe Critic / Repair
    ↓
Probe Execution
    ↓
Evidence
    ↓
Final Verdict
```

## Results at a Glance

Across 10 independent requirement-validation cases:

- **97** independent evaluator tests
- **64/97 (66.0%)** passed by the baseline implementations
- **33** failing evaluator scenarios
- **26** unique requirement defects
- **26/26** unique defects detected by SpecGuard
- **100% unique-defect recall**
- **6/6** core project tests passing

## Why SpecGuard?

Passing existing developer tests does not necessarily mean that an implementation satisfies the complete written requirement.

In the baseline Case 01 evaluation:

- Developer tests passed: **2/2**
- Independent evaluator passed: **3/10**
- Independent evaluator failures: **7**

SpecGuard generated execution evidence exposing the missing requirement behaviors behind those failures.

This demonstrates the central principle of the project:

> Passing developer tests is not sufficient evidence of full requirement satisfaction.

## Quick Start

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the core project tests:

```bash
pytest tests -v
```

Run an individual evaluation case:

```bash
cd evaluation/cases/case_01
pytest test_app.py -v
pytest evaluator_test.py -v
```

Return to the project root:

```bash
cd ../../..
```

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

This creates a deterministic validation layer between agent-generated reasoning and execution.

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

## Key Technical Contributions

- Requirement-driven verification rather than test-only validation
- Semantic decomposition of natural-language requirements
- Agent-generated executable verification probes
- Deterministic probe validation and repair
- Boundary and adversarial verification
- Typed-input verification
- Multi-argument verification
- Execution-grounded final verdicts
- Explicit `inconclusive` handling for execution failures
- Evidence and trajectory capture for auditable agentic development
- Evaluation across 10 independent benchmark cases

## Evaluation

SpecGuard was evaluated across 10 independent requirement-validation cases.

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

Across the 10 cases:

- Independent evaluator tests: **97**
- Baseline tests passed: **64**
- Baseline pass rate: **66.0%**
- Failing evaluator scenarios: **33**
- Unique requirement defects: **26**
- Defects detected by SpecGuard: **26**
- Unique-defect recall: **100%**

Multiple evaluator failures can correspond to the same underlying missing requirement behavior. For that reason, defect recall is calculated using unique requirement defects rather than raw failing-test count.

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
- generalization failures and subsequent improvements
- execution-error handling evidence

This provides an auditable trail showing how the solution evolved and how verification decisions were reached.

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

The benchmark is intentionally designed so that developer tests can pass while additional requirement behaviors remain untested.

## Execution Verdict Semantics

SpecGuard separates agent reasoning from executable verification evidence:

```text
Agent reasoning
      ↓
Generated probes
      ↓
Deterministic validation / repair
      ↓
Probe execution
      ↓
Evidence
      ↓
Final verdict
```

An execution error does not automatically constitute a requirement violation.

If every probe fails to execute and no usable execution evidence is produced, the criterion is reported as:

```text
inconclusive
```

This prevents invocation or execution failures from being incorrectly classified as implementation defects.

## Limitations

- Verification quality depends on the quality and completeness of the written requirements.
- Semantic decomposition and probe generation depend partly on LLM reasoning.
- The benchmark focuses on deterministic function-level validation cases.
- The current benchmark does not represent the full complexity of production-scale distributed systems.
- The 100% recall result applies specifically to the 26 unique defects represented in this benchmark and should not be interpreted as universal verification accuracy.
- `inconclusive` results require further investigation because they contain insufficient executable evidence.

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
```

## Testing

Run the core test suite:

```bash
pytest tests -v
```

Current result:

```text
6 passed
```

The independent evaluator suites intentionally contain failing scenarios because the benchmark implementations contain seeded requirement gaps. Those failures are used to evaluate whether SpecGuard can discover the missing behaviors.

## Reproducibility

Aggregate benchmark results are available at:

`evaluation/results/aggregate_metrics.md`

Development and verification traces are available under:

`trajectories/`

Individual benchmark cases can be reproduced from their corresponding directories under:

`evaluation/cases/`

## Conclusion

SpecGuard demonstrates an evidence-driven approach to requirement verification.

It combines semantic requirement decomposition, agent-generated probes, deterministic validation and repair, direct execution, and evidence-grounded verdicts to independently examine whether implementation behavior matches written requirements.

The central finding of the benchmark is:

> Passing developer tests does not necessarily demonstrate complete requirement satisfaction.