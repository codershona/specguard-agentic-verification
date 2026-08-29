from app import validate_email


def test_valid_email():
    assert validate_email("user@example.com") == "VALID"


def test_missing_at():
    assert validate_email("userexample.com") == "INVALID_EMAIL"


def test_multiple_at():
    assert validate_email("user@@example.com") == "INVALID_EMAIL"


def test_missing_local_part():
    assert validate_email("@example.com") == "INVALID_EMAIL"


def test_missing_domain_part():
    assert validate_email("user@") == "INVALID_EMAIL"


def test_domain_without_dot():
    assert validate_email("user@example") == "INVALID_EMAIL"


def test_email_with_space():
    assert validate_email("user @example.com") == "INVALID_EMAIL"


def test_non_ascii_email():
    assert validate_email("usér@example.com") == "INVALID_EMAIL"


def test_valid_result():
    assert validate_email("hello@test.org") == "VALID"