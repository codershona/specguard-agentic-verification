from app import validate_withdrawal


def test_valid_withdrawal():
    assert validate_withdrawal(100, 500) == "APPROVED"


def test_minimum_boundary():
    assert validate_withdrawal(10, 500) == "APPROVED"


def test_maximum_boundary():
    assert validate_withdrawal(500, 500) == "APPROVED"


def test_below_minimum():
    assert validate_withdrawal(9, 500) == "INVALID_WITHDRAWAL"


def test_above_maximum():
    assert validate_withdrawal(501, 1000) == "INVALID_WITHDRAWAL"


def test_string_amount():
    assert validate_withdrawal("100", 500) == "INVALID_WITHDRAWAL"


def test_string_balance():
    assert validate_withdrawal(100, "500") == "INVALID_WITHDRAWAL"


def test_exceeds_balance():
    assert validate_withdrawal(101, 100) == "DECLINED"


def test_boolean_amount():
    assert validate_withdrawal(True, 500) == "INVALID_WITHDRAWAL"


def test_boolean_balance():
    assert validate_withdrawal(100, True) == "INVALID_WITHDRAWAL"
