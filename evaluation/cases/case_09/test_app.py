from app import validate_coupon


def test_valid_coupon():
    assert validate_coupon("SAVE1234") == "VALID_COUPON"


def test_wrong_length_is_invalid():
    assert validate_coupon("SAVE123") == "INVALID_COUPON"
