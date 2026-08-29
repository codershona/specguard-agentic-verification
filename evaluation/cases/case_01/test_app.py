from app import validate_username


def test_valid_username():
    assert validate_username("falguni_01") == "VALID"


def test_username_too_short():
    assert validate_username("ab") == "INVALID_USERNAME"