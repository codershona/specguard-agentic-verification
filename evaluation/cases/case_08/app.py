def validate_transfer(amount, balance):
    if not isinstance(amount, (int, float)):
        return "INVALID_TRANSFER"

    if not isinstance(balance, (int, float)):
        return "INVALID_TRANSFER"

    if amount <= 0:
        return "INVALID_TRANSFER"

    if balance < 0:
        return "INVALID_TRANSFER"

    return "APPROVED"
