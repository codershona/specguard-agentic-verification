from pathlib import Path

from specguard.execution import execute_verification_results
from specguard.parser import parse_requirement_file
from specguard.semantic_decomposer import semantic_decompose
from specguard.verifier import verify_file


CASE_DIR = Path("evaluation/cases/case_01")


def main() -> None:
    requirement_path = CASE_DIR / "requirement.md"
    source_path = CASE_DIR / "app.py"

    specification = parse_requirement_file(
        requirement_path
    )

    criteria = semantic_decompose(
        specification
    )

    verification_results = verify_file(
        source_path,
        criteria,
    )

    executed_results = execute_verification_results(
        source_path=source_path,
        function_name="validate_username",
        verification_results=verification_results,
    )

    print("\n=== SPECGUARD CASE 01 EVALUATION ===\n")

    for result in executed_results:
        print(
            result["criterion_id"],
            "->",
            result["final_verdict"].upper(),
        )

    violated_criteria = [
        result
        for result in executed_results
        if result["final_verdict"] == "violated"
    ]

    satisfied_criteria = [
        result
        for result in executed_results
        if result["final_verdict"] == "satisfied"
    ]

    total_criteria = len(executed_results)
    detected_violations = len(violated_criteria)

    detection_rate = (
        detected_violations / total_criteria * 100
        if total_criteria
        else 0
    )

    print("\n=== SUMMARY ===\n")
    print("Total acceptance criteria:", total_criteria)
    print("Detected violations:", detected_violations)
    print(
        "Satisfied criteria:",
        len(satisfied_criteria),
    )
    print(
        "Criterion violation detection rate:",
        f"{detection_rate:.1f}%",
    )

    evaluator_failures = {
    "maximum_length": "AC-01",
    "hyphen_rejected": "AC-02",
    "space_rejected": "AC-02",
    "non_ascii_rejected": "AC-02",
    "leading_underscore": "AC-03",
    "trailing_underscore": "AC-04",
    "consecutive_underscores": "AC-05",
}

    violated_ids = {
        result["criterion_id"]
        for result in executed_results
        if result["final_verdict"] == "violated"
    }

    detected_evaluator_failures = sum(
        1
        for criterion_id in evaluator_failures.values()
        if criterion_id in violated_ids
    )

    total_evaluator_failures = len(evaluator_failures)

    defect_recall = (
        detected_evaluator_failures
        / total_evaluator_failures
        * 100
    )

    print("\n=== EVALUATOR DEFECT RECALL ===\n")
    print(
        "Evaluator failures:",
        total_evaluator_failures,
    )
    print(
        "Failures detected by SpecGuard:",
        detected_evaluator_failures,
    )
    print(
        "Defect recall:",
        f"{defect_recall:.1f}%",
    )


if __name__ == "__main__":
    main()