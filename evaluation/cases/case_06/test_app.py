from app import validate_discount


def test_valid_discount():
    assert validate_discount(20) == "VALID"


def test_negative_discount_is_invalid():
    assert validate_discount(-1) == "INVALID_DISCOUNT"
