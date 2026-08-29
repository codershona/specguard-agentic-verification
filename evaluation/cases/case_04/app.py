def validate_quantity(quantity):
    if not isinstance(quantity, int):
        return "INVALID_QUANTITY"

    if quantity < 1:
        return "INVALID_QUANTITY"

    return "VALID"