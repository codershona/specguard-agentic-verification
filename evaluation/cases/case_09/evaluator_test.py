from app import validate_coupon


def test_valid_coupon():
    assert validate_coupon("SAVE1234") == "VALID_COUPON"


def test_another_valid_coupon():
    assert validate_coupon("SAVE9999") == "VALID_COUPON"


def test_too_short():
    assert validate_coupon("SAVE123") == "INVALID_COUPON"


def test_too_long():
    assert validate_coupon("SAVE12345") == "INVALID_COUPON"


def test_non_string():
    assert validate_coupon(12345678) == "INVALID_COUPON"


def test_special_character():
    assert validate_coupon("SAVE12!4") == "INVALID_COUPON"


def test_lowercase_invalid():
    assert validate_coupon("save1234") == "INVALID_COUPON"


def test_mixed_case_invalid():
    assert validate_coupon("Save1234") == "INVALID_COUPON"


def test_wrong_prefix():
    assert validate_coupon("TEST1234") == "INVALID_COUPON"


def test_numeric_prefix():
    assert validate_coupon("12345678") == "INVALID_COUPON"
