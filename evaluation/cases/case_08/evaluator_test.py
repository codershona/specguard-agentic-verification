from app import validate_transfer

def test_valid_transfer():
    assert validate_transfer(50, 100) == "APPROVED"

def test_equal_balance():
    assert validate_transfer(100, 100) == "APPROVED"

def test_zero_amount_invalid():
    assert validate_transfer(0, 100) == "INVALID_TRANSFER"

def test_negative_amount_invalid():
    assert validate_transfer(-1, 100) == "INVALID_TRANSFER"

def test_negative_balance_invalid():
    assert validate_transfer(10, -1) == "INVALID_TRANSFER"

def test_amount_exceeds_balance():
    assert validate_transfer(101, 100) == "DECLINED"

def test_float_transfer():
    assert validate_transfer(25.5, 100.0) == "APPROVED"

def test_string_amount_invalid():
    assert validate_transfer("50", 100) == "INVALID_TRANSFER"

def test_boolean_amount_invalid():
    assert validate_transfer(True, 100) == "INVALID_TRANSFER"

def test_boolean_balance_invalid():
    assert validate_transfer(50, True) == "INVALID_TRANSFER"
