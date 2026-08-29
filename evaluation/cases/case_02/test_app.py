from app import validate_password


def test_valid_password():
    assert validate_password("Password1!") == "VALID"


def test_too_short_password():
    assert validate_password("Pass1!") == "INVALID_PASSWORD"