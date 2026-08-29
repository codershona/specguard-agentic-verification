from app import check_username_availability

def test_available_username():
    assert check_username_availability("newuser") == "AVAILABLE"

def test_taken_username():
    assert check_username_availability("admin") == "UNAVAILABLE"
