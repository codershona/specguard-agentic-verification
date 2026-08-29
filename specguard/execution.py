import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any


def load_module_from_file(
    source_path: str | Path,
) -> ModuleType:
    source_path = Path(source_path)

    spec = importlib.util.spec_from_file_location(
        "specguard_target",
        source_path,
    )

    if spec is None or spec.loader is None:
        raise ValueError(
            f"Could not load source file: {source_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def execute_probe(
    source_path: str | Path,
    function_name: str,
    probe: dict[str, Any],
) -> dict[str, Any]:
    if "input" not in probe:
        raise ValueError(
            "Probe is missing 'input'."
        )

    if "expected" not in probe:
        raise ValueError(
            "Probe is missing 'expected'."
        )

    module = load_module_from_file(source_path)

    if not hasattr(module, function_name):
        raise ValueError(
            f"Function '{function_name}' was not found "
            f"in {source_path}."
        )

    target_function = getattr(
        module,
        function_name,
    )

    test_input = probe["input"]
    expected = probe["expected"]

    try:
        if isinstance(test_input, dict):
         actual = target_function(**test_input)
        else:
         actual = target_function(test_input)

        return {
            "input": test_input,
            "expected": expected,
            "actual": actual,
            "matched": actual == expected,
            "error": None,
        }

    except Exception as exc:
        return {
            "input": test_input,
            "expected": expected,
            "actual": None,
            "matched": False,
            "error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }


def execute_verification_results(
    source_path: str | Path,
    function_name: str,
    verification_results: list[dict],
) -> list[dict]:
    executed_results = []

    for verification in verification_results:
        probe_results = []

        for probe in verification["probes"]:
            result = execute_probe(
                source_path=source_path,
                function_name=function_name,
                probe=probe,
            )

            probe_results.append(result)

        confirmed_violation = any(
            not probe["matched"]
            and probe["error"] is None
            for probe in probe_results
        )

        successful_executions = [
            probe
            for probe in probe_results
            if probe["error"] is None
        ]

        if confirmed_violation:
            final_verdict = "violated"
        elif not successful_executions:
            final_verdict = "inconclusive"
        else:
            final_verdict = "satisfied"

        executed_results.append(
            {
                "criterion_id": verification[
                    "criterion_id"
                ],
                "requirement_number": verification[
                    "requirement_number"
                ],
                "agent_verdict": verification[
                    "verdict"
                ],
                "final_verdict": final_verdict,
                "reason": verification[
                    "reason"
                ],
                "probes": probe_results,
                "confirmed_violation": confirmed_violation,
            }
        )

    return executed_results