from app import validate_discount


def test_zero_is_valid():
    assert validate_discount(0) == "VALID"


def test_integer_discount_is_valid():
    assert validate_discount(50) == "VALID"


def test_float_discount_is_valid():
    assert validate_discount(25.5) == "VALID"


def test_hundred_is_valid():
    assert validate_discount(100) == "VALID"


def test_negative_integer_is_invalid():
    assert validate_discount(-1) == "INVALID_DISCOUNT"


def test_negative_float_is_invalid():
    assert validate_discount(-0.1) == "INVALID_DISCOUNT"


def test_above_hundred_is_invalid():
    assert validate_discount(101) == "INVALID_DISCOUNT"


def test_string_is_invalid():
    assert validate_discount("50") == "INVALID_DISCOUNT"


def test_true_is_invalid():
    assert validate_discount(True) == "INVALID_DISCOUNT"


def test_false_is_invalid():
    assert validate_discount(False) == "INVALID_DISCOUNT"
