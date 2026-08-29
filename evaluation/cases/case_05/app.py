def validate_date_range(start_day, end_day):
    if not isinstance(start_day, int):
        return "INVALID_DATE_RANGE"

    if not isinstance(end_day, int):
        return "INVALID_DATE_RANGE"

    if start_day < 1:
        return "INVALID_DATE_RANGE"

    if start_day > end_day:
        return "INVALID_DATE_RANGE"

    return "VALID"