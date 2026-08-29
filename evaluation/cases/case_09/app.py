def validate_coupon(code):
    if not isinstance(code, str):
        return "INVALID_COUPON"

    if len(code) != 8:
        return "INVALID_COUPON"

    if not code.isalnum():
        return "INVALID_COUPON"

    return "VALID_COUPON"
