# Withdrawal Validation Requirements

1. Withdrawal amount must be a number.
2. Withdrawal amount must be at least 10.
3. Withdrawal amount must not exceed 500.
4. Account balance must be a number.
5. Withdrawal amount must not exceed the account balance.
6. Boolean values must not be accepted as withdrawal amounts or account balances.
7. Return APPROVED when all requirements are satisfied.
8. Return DECLINED when the withdrawal amount exceeds the account balance.
9. Return INVALID_WITHDRAWAL when any input validation requirement is violated.
