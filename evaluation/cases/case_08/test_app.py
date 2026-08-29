from app import validate_transfer

def test_valid_transfer():
    assert validate_transfer(50, 100) == "APPROVED"

def test_zero_amount_is_invalid():
    assert validate_transfer(0, 100) == "INVALID_TRANSFER"
