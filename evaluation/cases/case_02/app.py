def validate_password(password: str) -> str:
    if len(password) < 8:
        return "INVALID_PASSWORD"

    if not any(char.isupper() for char in password):
        return "INVALID_PASSWORD"

    if not any(char.islower() for char in password):
        return "INVALID_PASSWORD"

    return "VALID"