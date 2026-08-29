def validate_username(username: str) -> str:
    """Validate a username for account registration."""

    if len(username) < 3:
        return "INVALID_USERNAME"

    return "VALID"