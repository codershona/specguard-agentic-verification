# Booking Date Range Validation Requirements

1. Start day must be an integer.
2. End day must be an integer.
3. Start day must be at least 1.
4. End day must not exceed 31.
5. Start day must not be greater than end day.
6. Start day and end day must not be boolean values.
7. Return VALID when all requirements are satisfied.
8. Return INVALID_DATE_RANGE when any requirement is violated.