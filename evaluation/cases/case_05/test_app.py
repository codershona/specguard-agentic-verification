from app import validate_date_range


def test_valid_date_range():
    assert validate_date_range(5, 10) == "VALID"


def test_start_before_one_is_invalid():
    assert validate_date_range(0, 10) == "INVALID_DATE_RANGE"