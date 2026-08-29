# Reproduction Guide

This guide explains how to reproduce the SpecGuard baseline, agentic verification workflow, and evaluation results from a clean environment.

## 1. Environment

The project was validated with:

- Python 3.14.4
- Ollama 0.33.2
- Ollama model: `qwen3:4b`
- pytest 9.1.1
- pluggy 1.6.0
- iniconfig 2.3.0
- packaging 26.3
- Pygments 2.21.0

The workflow uses a local Ollama model and does not require a paid external LLM API.

## 2. Clean Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/codershona/specguard-agentic-verification.git
cd specguard-agentic-verification
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install Ollama separately if it is not already installed.

Pull the required local model:

```bash
ollama pull qwen3:4b
```

Confirm that the model is available:

```bash
ollama list
```

Expected model:

```text
qwen3:4b
```

## 3. Run the Core Project Tests

From the repository root:

```bash
pytest tests -v
```

Expected result:

```text
6 passed
```

These tests cover requirement parsing, deterministic decomposition, semantic decomposition, verification behavior, probe execution, and execution-error handling.

## 4. Reproduce the Baseline

Each benchmark case contains:

- `requirement.md` — written specification
- `app.py` — target implementation
- `test_app.py` — developer-written tests
- `evaluator_test.py` — independent evaluator

For Case 01:

```bash
cd evaluation/cases/case_01
pytest test_app.py -v
pytest evaluator_test.py -v
cd ../../..
```

Expected Case 01 baseline results:

```text
Developer tests: 2/2 passed
Independent evaluator: 3/10 passed
Independent evaluator failures: 7
```

The developer tests therefore pass even though the independent evaluator exposes additional missing requirement behavior.

## 5. Run SpecGuard End to End

From the repository root:

```bash
PYTHONPATH=. python evaluation/score_case_01.py
```

The command performs:

```text
Requirement
    ↓
Requirement Parser
    ↓
Semantic Decomposer
    ↓
Verification Agent
    ↓
Deterministic Probe Validation / Repair
    ↓
Probe Execution
    ↓
Evidence
    ↓
Final Verdict
```

Expected Case 01 result:

```text
AC-01 -> VIOLATED
AC-02 -> VIOLATED
AC-03 -> VIOLATED
AC-04 -> VIOLATED
AC-05 -> VIOLATED
AC-06 -> SATISFIED
AC-07 -> SATISFIED
```

Expected summary:

```text
Total acceptance criteria: 7
Detected violations: 5
Satisfied criteria: 2
Criterion violation detection rate: 71.4%
```

Expected evaluator comparison:

```text
Evaluator failures: 7
Failures detected by SpecGuard: 7
Defect recall: 100.0%
```

The seven failing evaluator scenarios in Case 01 map to five distinct acceptance-criterion defect dimensions. Raw failing-test count and unique-defect count should therefore not be treated as identical metrics.

## 6. Runtime

A representative Case 01 run can be timed with:

```bash
/usr/bin/time -p env PYTHONPATH=. python evaluation/score_case_01.py
```

Measured development-machine result:

```text
real 27.87
user 0.08
sys 0.04
```

Runtime depends on hardware and local Ollama inference performance.

## 7. Cost

SpecGuard uses the local Ollama `qwen3:4b` model.

External LLM API cost for the reproduced workflow:

```text
$0
```

The user provides the compute resources required to run the local model.

## 8. Reproduce Individual Benchmark Cases

Developer and evaluator behavior can be inspected independently for every case.

Example:

```bash
cd evaluation/cases/case_05
pytest test_app.py -v
pytest evaluator_test.py -v
cd ../../..
```

Repeat with `case_01` through `case_10`.

The evaluator tests are executed independently and are not provided to the verification agent as hidden guidance during SpecGuard verification.

## 9. Aggregate Evaluation Results

Final benchmark results are recorded in:

```text
evaluation/results/aggregate_metrics.md
```

Aggregate results:

- Evaluation cases: 10
- Independent evaluator tests: 97
- Baseline tests passed: 64/97
- Baseline evaluator pass rate: 66.0%
- Failing evaluator scenarios: 33
- Unique requirement defects: 26
- Unique defects detected by SpecGuard: 26/26
- Primary metric — unique-defect recall: 100%

The baseline evaluator pass rate and SpecGuard unique-defect recall measure different aspects of the experiment and should not be interpreted as a direct 66.0% to 100% accuracy comparison.

## 10. Evidence and Agent Trajectories

Representative development and verification evidence is available under:

```text
trajectories/
```

Run:

```bash
cat trajectories/README.md
```

to view the trajectory index.

Evidence includes:

- semantic decomposition iterations
- initial verification attempts
- generated probes
- deterministic repairs
- execution results
- final verdicts
- generalization failures
- typed-input failures
- multi-argument verification
- transaction verification
- execution-error handling

## 11. Expected Final State

After setup and reproduction:

```bash
pytest tests -v
```

should report:

```text
6 passed
```

The intentionally defective benchmark implementations may still produce failures in their independent evaluator suites. Those failures are expected and form the evaluation target for SpecGuard.

## 12. Notes on Reproducibility

LLM-generated probe text can vary between local runs even with deterministic configuration.

For this reason, SpecGuard does not rely solely on the model's self-reported verdict.

Generated probes are validated and repaired before execution, and final requirement verdicts are based on executable evidence.

If all generated probes fail to execute, the final result is:

```text
inconclusive
```

rather than incorrectly reporting either satisfaction or violation.
