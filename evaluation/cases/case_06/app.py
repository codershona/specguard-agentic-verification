def validate_discount(discount):
    if not isinstance(discount, (int, float)):
        return "INVALID_DISCOUNT"

    if discount < 0:
        return "INVALID_DISCOUNT"

    return "VALID"
