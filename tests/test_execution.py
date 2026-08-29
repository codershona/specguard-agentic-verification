from specguard.execution import execute_probe, execute_verification_results


def test_execute_probe_matches_expected():
    result = execute_probe(
        source_path="evaluation/cases/case_01/app.py",
        function_name="validate_username",
        probe={
            "input": "ab",
            "expected": "INVALID_USERNAME",
        },
    )

    assert result["input"] == "ab"
    assert result["expected"] == "INVALID_USERNAME"
    assert result["actual"] == "INVALID_USERNAME"
    assert result["matched"] is True
    assert result["error"] is None

def test_execute_verification_results_marks_all_errors_inconclusive():
    verification_results = [
        {
            "criterion_id": "AC-TEST",
            "requirement_number": 1,
            "verdict": "satisfied",
            "reason": "Test execution error handling",
            "probes": [
                {
                    "input": {"unexpected": "input"},
                    "expected": "INVALID_USERNAME",
                }
            ],
        }
    ]

    results = execute_verification_results(
        source_path="evaluation/cases/case_01/app.py",
        function_name="validate_username",
        verification_results=verification_results,
    )

    assert results[0]["confirmed_violation"] is False
    assert results[0]["final_verdict"] == "inconclusive"
    assert results[0]["probes"][0]["error"] is not None