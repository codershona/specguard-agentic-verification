from pathlib import Path

from specguard.execution import execute_verification_results
from specguard.parser import parse_requirement_file
from specguard.semantic_decomposer import semantic_decompose
from specguard.verifier import verify_file


CASE_DIR = Path("evaluation/cases/case_02")


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
        function_name="validate_password",
        verification_results=verification_results,
    )

    print("\n=== SPECGUARD CASE 02 EVALUATION ===\n")

    for result in executed_results:
        print(
            result["criterion_id"],
            "->",
            result["final_verdict"].upper(),
        )


if __name__ == "__main__":
    main()