# Username Availability Validation Requirements

1. Username must be a string.
2. Username must contain at least 3 characters.
3. Username must contain no more than 15 characters.
4. Username comparison must be case-insensitive when checking whether it is already taken.
5. Return AVAILABLE when the username is valid and not already taken.
6. Return UNAVAILABLE when the username is already taken.
7. Return INVALID_USERNAME when the username violates any validation requirement.
