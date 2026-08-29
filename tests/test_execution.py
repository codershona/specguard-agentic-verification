from specguard.execution import execute_probe


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