TAKEN_USERNAMES = {"admin", "john", "alice"}

def check_username_availability(username):
    if not isinstance(username, str):
        return "INVALID_USERNAME"

    if len(username) < 3:
        return "INVALID_USERNAME"

    if username in TAKEN_USERNAMES:
        return "UNAVAILABLE"

    return "AVAILABLE"
