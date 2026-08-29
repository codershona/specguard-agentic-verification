def validate_withdrawal(amount, balance):
    if not isinstance(amount, (int, float)):
        return "INVALID_WITHDRAWAL"

    if not isinstance(balance, (int, float)):
        return "INVALID_WITHDRAWAL"

    if amount < 10:
        return "INVALID_WITHDRAWAL"

    if amount > 500:
        return "INVALID_WITHDRAWAL"

    return "APPROVED"
