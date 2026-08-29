from app import validate_withdrawal


def test_valid_withdrawal():
    assert validate_withdrawal(100, 500) == "APPROVED"


def test_below_minimum_is_invalid():
    assert validate_withdrawal(9, 500) == "INVALID_WITHDRAWAL"
