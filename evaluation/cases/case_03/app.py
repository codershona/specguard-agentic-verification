def validate_email(email: str) -> str:
    if email.count("@") != 1:
        return "INVALID_EMAIL"

    local, domain = email.split("@")

    if not local or not domain:
        return "INVALID_EMAIL"

    return "VALID"