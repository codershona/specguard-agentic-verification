from app import validate_quantity


def test_valid_minimum():
    assert validate_quantity(1) == "VALID"


def test_valid_typical():
    assert validate_quantity(50) == "VALID"


def test_valid_maximum():
    assert validate_quantity(100) == "VALID"


def test_zero_invalid():
    assert validate_quantity(0) == "INVALID_QUANTITY"


def test_negative_invalid():
    assert validate_quantity(-1) == "INVALID_QUANTITY"


def test_exceeds_maximum_invalid():
    assert validate_quantity(101) == "INVALID_QUANTITY"


def test_float_invalid():
    assert validate_quantity(10.5) == "INVALID_QUANTITY"


def test_string_invalid():
    assert validate_quantity("10") == "INVALID_QUANTITY"


def test_boolean_invalid():
    assert validate_quantity(True) == "INVALID_QUANTITY"