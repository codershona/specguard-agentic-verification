from app import validate_quantity


def test_valid_quantity():
    assert validate_quantity(10) == "VALID"


def test_zero_is_invalid():
    assert validate_quantity(0) == "INVALID_QUANTITY"