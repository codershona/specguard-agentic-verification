from app import validate_email


def test_valid_email():
    assert validate_email("user@example.com") == "VALID"


def test_missing_at_is_invalid():
    assert validate_email("userexample.com") == "INVALID_EMAIL"