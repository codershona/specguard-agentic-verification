from app import check_username_availability

def test_available_username():
    assert check_username_availability("newuser") == "AVAILABLE"

def test_minimum_length():
    assert check_username_availability("abc") == "AVAILABLE"

def test_too_short():
    assert check_username_availability("ab") == "INVALID_USERNAME"

def test_maximum_length():
    assert check_username_availability("abcdefghijklmno") == "AVAILABLE"

def test_too_long():
    assert check_username_availability("abcdefghijklmnop") == "INVALID_USERNAME"

def test_taken_admin():
    assert check_username_availability("admin") == "UNAVAILABLE"

def test_taken_username_case_insensitive():
    assert check_username_availability("ADMIN") == "UNAVAILABLE"

def test_taken_john_case_insensitive():
    assert check_username_availability("JoHn") == "UNAVAILABLE"

def test_non_string_integer():
    assert check_username_availability(12345) == "INVALID_USERNAME"

def test_non_string_boolean():
    assert check_username_availability(True) == "INVALID_USERNAME"
