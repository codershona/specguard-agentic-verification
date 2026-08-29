from app import validate_date_range


def test_valid_single_day():
    assert validate_date_range(1, 1) == "VALID"


def test_valid_full_range():
    assert validate_date_range(1, 31) == "VALID"


def test_start_below_minimum_invalid():
    assert validate_date_range(0, 10) == "INVALID_DATE_RANGE"


def test_start_negative_invalid():
    assert validate_date_range(-1, 10) == "INVALID_DATE_RANGE"


def test_end_exceeds_maximum_invalid():
    assert validate_date_range(10, 32) == "INVALID_DATE_RANGE"


def test_start_greater_than_end_invalid():
    assert validate_date_range(20, 10) == "INVALID_DATE_RANGE"


def test_non_integer_start_invalid():
    assert validate_date_range("5", 10) == "INVALID_DATE_RANGE"


def test_non_integer_end_invalid():
    assert validate_date_range(5, "10") == "INVALID_DATE_RANGE"


def test_boolean_start_invalid():
    assert validate_date_range(True, 10) == "INVALID_DATE_RANGE"


def test_boolean_end_invalid():
    assert validate_date_range(5, False) == "INVALID_DATE_RANGE"