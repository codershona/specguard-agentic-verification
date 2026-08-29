# Transfer Validation Requirements

1. Transfer amount must be a number.
2. Transfer amount must be greater than 0.
3. Account balance must be a number.
4. Account balance must be at least 0.
5. Transfer amount must not exceed the account balance.
6. Boolean values must not be accepted as transfer amounts or account balances.
7. Return APPROVED when all requirements are satisfied.
8. Return DECLINED when the transfer amount exceeds the account balance.
9. Return INVALID_TRANSFER when any input validation requirement is violated.
