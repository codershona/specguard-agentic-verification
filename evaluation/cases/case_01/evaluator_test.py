from app import validate_username


def test_minimum_length_boundary():
    assert validate_username("abc") == "VALID"


def test_maximum_length_boundary():
    assert validate_username("abcdefghijklmnopqrst") == "VALID"


def test_exceeds_maximum_length():
    assert validate_username("abcdefghijklmnopqrstu") == "INVALID_USERNAME"


def test_cannot_start_with_underscore():
    assert validate_username("_falguni") == "INVALID_USERNAME"


def test_cannot_end_with_underscore():
    assert validate_username("falguni_") == "INVALID_USERNAME"


def test_consecutive_underscores_rejected():
    assert validate_username("falguni__01") == "INVALID_USERNAME"


def test_hyphen_rejected():
    assert validate_username("falguni-01") == "INVALID_USERNAME"


def test_space_rejected():
    assert validate_username("falguni 01") == "INVALID_USERNAME"


def test_non_ascii_letters_rejected():
    assert validate_username("fálguni") == "INVALID_USERNAME"


def test_digits_and_single_underscore_allowed():
    assert validate_username("user_2026") == "VALID"