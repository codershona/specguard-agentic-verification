# Case 01 — Username Validation

## Requirement

Implement username validation for account registration.

A valid username must:

1. Be between 3 and 20 characters inclusive.
2. Contain only ASCII letters (`A-Z`, `a-z`), digits (`0-9`), or underscore (`_`).
3. Not begin or end with an underscore.
4. Not contain consecutive underscores.
5. Return `VALID` when all requirements are satisfied.
6. Return `INVALID_USERNAME` when any requirement is violated.

## Acceptance Examples

- `falguni_01` → `VALID`
- `ab` → `INVALID_USERNAME`
- `this_username_is_far_too_long` → `INVALID_USERNAME`
- `_falguni` → `INVALID_USERNAME`
- `falguni_` → `INVALID_USERNAME`
- `falguni__01` → `INVALID_USERNAME`
- `falguni-01` → `INVALID_USERNAME`