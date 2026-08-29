from app import validate_password


def test_minimum_length():
    assert validate_password("Password1!") == "VALID"


def test_maximum_length():
    assert validate_password("Password12345!") == "VALID"


def test_exceeds_maximum_length():
    assert validate_password("Password123456!") == "INVALID_PASSWORD"


def test_uppercase_required():
    assert validate_password("password1!") == "INVALID_PASSWORD"


def test_lowercase_required():
    assert validate_password("PASSWORD1!") == "INVALID_PASSWORD"


def test_digit_required():
    assert validate_password("Password!") == "INVALID_PASSWORD"


def test_special_character_required():
    assert validate_password("Password1") == "INVALID_PASSWORD"


def test_space_rejected():
    assert validate_password("Pass word1!") == "INVALID_PASSWORD"


def test_valid_password():
    assert validate_password("Secure1!") == "VALID"