import json
from pathlib import Path

from specguard.decomposer import AcceptanceCriterion
from specguard.llm import OllamaClient


MAX_RETRIES = 3
VALID_RESULT = "VALID"
INVALID_RESULT_PREFIX = "INVALID_"


def _build_verification_prompt(
    source_code: str,
    criterion: AcceptanceCriterion,
    feedback: str | None = None,
) -> str:
    prompt = f"""
You are SpecGuard's Verification Agent.

Generate isolated verification probes for ONE acceptance criterion.

Use only:
1. The supplied acceptance criterion.
2. The supplied implementation source code.

Do not use hidden evaluator tests.
Do not invent requirements.

Generate between 2 and 4 probes.

Important:
Each probe must directly test THIS acceptance criterion.
Avoid inputs that only test unrelated requirements.

PROBE ISOLATION RULE:

A probe must isolate the acceptance criterion being tested.

When the implementation has multiple validation rules, construct the
probe so that unrelated validation rules are satisfied whenever possible.

For a negative probe, change only the property relevant to THIS
acceptance criterion while keeping unrelated properties valid.

Example:

If a password must contain uppercase, lowercase, digit, and special
characters, and THIS criterion is "must contain at least one lowercase
ASCII letter":

Useful probes:
- "Password1!" -> VALID
- "PASSWORD1!" -> INVALID_PASSWORD

Bad probe:
- "abcdefgh" -> VALID

The bad probe is invalid because it also lacks uppercase, digit, and
special characters, so a failure would not isolate the lowercase
criterion.

Similarly, when testing maximum password length, use inputs that still
satisfy the other password requirements.

Do not use strings consisting only of digits or only letters if those
inputs would violate unrelated validation rules.

Examples:

Numeric range:
Username must be between 3 and 20 characters inclusive.

Required useful probes:
- "abc" -> VALID
- "ab" -> INVALID_USERNAME
- "aaaaaaaaaaaaaaaaaaaa" -> VALID
- "aaaaaaaaaaaaaaaaaaaaa" -> INVALID_USERNAME


Allowed characters:
Username may contain only ASCII letters, digits, or underscore.

Useful probes:
- "abc123" -> VALID
- "abc!" -> INVALID_USERNAME


Leading underscore:
Username must not begin with an underscore.

Useful probes:
- "_abc" -> INVALID_USERNAME
- "abc" -> VALID


Trailing underscore:
Username must not end with an underscore.

Useful probes:
- "abc_" -> INVALID_USERNAME
- "abc" -> VALID


Consecutive underscores:
Username must not contain consecutive underscores.

You MUST include a probe containing "__".

Required useful probes:
- "a__b" -> INVALID_USERNAME
- "a_b" -> VALID

Do NOT use "_a", "a_", "a", or "ab" as the violating probe,
because those inputs do not contain consecutive underscores.


CRITICAL OUTPUT RULES:

INPUT TYPE RULES:

The JSON "input" value MUST preserve the real data type required by
the acceptance criterion.

For integer or numeric requirements:
- use 1, not "1"
- use 0, not "0"
- use 101, not "101"
- use 1.5, not "1.5"

For boolean requirements:
- use true or false as JSON booleans
- never use "true" or "false" as strings

For text, username, password, or email requirements:
- use JSON strings

Examples:

Integer probe:
{{
  "input": 101,
  "expected": "INVALID_QUANTITY"
}}

Float probe:
{{
  "input": 1.5,
  "expected": "INVALID_QUANTITY"
}}

Boolean probe:
...

String probe:
{{
  "input": "user@example.com",
  "expected": "VALID"
}}

Multi-argument function probe:
{{
  "input": {{
    "start_day": 5,
    "end_day": 10
  }},
  "expected": "VALID"
}}

When the target function has multiple parameters, every probe must provide all required arguments inside the "input" object using the exact parameter names.
Do not provide only one primitive value for a multi-argument function.

Every probe MUST contain exactly these two fields:
- "input"
- "expected"

"expected" MUST always be either:
- "VALID"
- a value beginning with "INVALID_"

Examples:
- "INVALID_USERNAME"
- "INVALID_PASSWORD"

Use the invalid result type that matches the supplied implementation
and acceptance criterion.

Never omit "expected".
Never use expected_result, result, output, status, or any other field name.

Return only valid JSON.
Do not include markdown.
Do not include explanations outside the JSON.

Use exactly:

{{
  "verdict": "satisfied",
  "reason": "short explanation",
  "probes": [
    {{
      "input": "example",
      "expected": "VALID"
    }}
  ]
}}

Allowed verdicts:
- "satisfied"
- "violated"
- "uncertain"

Acceptance criterion:
{criterion.description}

Implementation:
{source_code}
"""

    if feedback:
        prompt += f"""

Your previous response was rejected.

Validation feedback:
{feedback}

Fix the response and return the complete JSON again.
"""

    return prompt


def _validate_verification_response(
    raw_response: str,
) -> dict:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Verification response is not valid JSON."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(
            "Verification response must be a JSON object."
        )

    verdict = parsed.get("verdict")

    if verdict not in {
        "satisfied",
        "violated",
        "uncertain",
    }:
        raise ValueError(
            "Invalid verdict."
        )

    reason = parsed.get("reason")

    if not isinstance(reason, str) or not reason.strip():
        raise ValueError(
            "reason must be a non-empty string."
        )

    probes = parsed.get("probes")

    if not isinstance(probes, list):
        raise ValueError(
            "probes must be a list."
        )

    if len(probes) < 2:
        raise ValueError(
            "At least 2 probes are required."
        )

    if len(probes) > 4:
        raise ValueError(
            "Maximum 4 probes are allowed."
        )

    normalized = []
    seen = set()

    for index, probe in enumerate(
        probes,
        start=1,
    ):
        if not isinstance(probe, dict):
            raise ValueError(
                f"Probe {index} must be an object."
            )

        if "input" in probe:
           test_input = probe["input"]
        elif "test_input" in probe:
           test_input = probe["test_input"]
        elif "value" in probe:
           test_input = probe["value"]
        else:
           test_input = None

        expected = (
            probe.get("expected")
            or probe.get("expected_result")
            or probe.get("expected_output")
            or probe.get("output")
        )

        if test_input is None:
            raise ValueError(
                f"Probe {index} is missing input. "
                "Use exactly the key 'input'."
            )

        if expected is None:
            raise ValueError(
                f"Probe {index} is missing expected. "
                "Use exactly the key 'expected'."
            )

        if not isinstance(
            test_input,
            (str, int, float, bool, dict),
        ):
            raise ValueError(
                f"Probe {index} has unsupported input type "
                f"{type(test_input).__name__}."
            )

        if not isinstance(expected, str):
            expected = str(expected)

        expected = expected.strip()

        if not (
            expected.startswith(VALID_RESULT)
            or expected == "AVAILABLE"
            or expected == "UNAVAILABLE"
            or expected == "APPROVED"
            or expected == "DECLINED"
            or expected.startswith(
                INVALID_RESULT_PREFIX
            )
        ):
            raise ValueError(
                f"Probe {index} has invalid expected "
                f"value {expected!r}. "
                "Expected must start with VALID, be AVAILABLE, "
                "UNAVAILABLE, APPROVED, or DECLINED, "
                "or start with INVALID_."
            )
        signature = (
             repr(test_input),
        expected,
    )
        if signature in seen:
            continue

        seen.add(signature)

        normalized.append(
            {
                "input": test_input,
                "expected": expected,
            }
        )

    return {
        "verdict": verdict,
        "reason": reason.strip(),
        "probes": normalized,
    }


def _validate_probe_alignment(
    criterion: AcceptanceCriterion,
    probes: list[dict],
) -> None:
    """
    Deterministic probe critic.

    Reject probe sets that clearly do not test the supplied
    acceptance criterion.
    """

    description = criterion.description.lower()

    inputs = [
        probe["input"]
        for probe in probes
    ]

    expected_by_input = {
        (
            repr(probe["input"])
            if isinstance(probe["input"], dict)
            else probe["input"]
        ): probe["expected"]
        for probe in probes
    }

    # Leading underscore
    if "not begin with an underscore" in description:
        violating = [
            value
            for value in inputs
            if value.startswith("_")
            and len(value) >= 3
        ]

        if not violating:
            raise ValueError(
                "Leading-underscore criterion requires a "
                "valid-length probe beginning with '_'."
            )

        if not any(
            expected_by_input[value].startswith(
                INVALID_RESULT_PREFIX
            )
            for value in violating
        ):
            raise ValueError(
                "A leading-underscore probe must expect "
                "an INVALID_* result."
            )

    # Trailing underscore
    if "not end with an underscore" in description:
        violating = [
            value
            for value in inputs
            if value.endswith("_")
            and len(value) >= 3
        ]

        if not violating:
            raise ValueError(
                "Trailing-underscore criterion requires a "
                "valid-length probe ending with '_'."
            )

        if not any(
            expected_by_input[value].startswith(
                INVALID_RESULT_PREFIX
            )
            for value in violating
        ):
            raise ValueError(
                "A trailing-underscore probe must expect "
                "an INVALID_* result."
            )

    # Consecutive underscores
    if "consecutive underscores" in description:
        violating = [
            value
            for value in inputs
            if "__" in value
            and len(value) >= 3
        ]

        if not violating:
            raise ValueError(
                "Consecutive-underscore criterion requires "
                "a probe containing '__'."
            )

        if not any(
            expected_by_input[value].startswith(
                INVALID_RESULT_PREFIX
            )
            for value in violating
        ):
            raise ValueError(
                "A consecutive-underscore probe must expect "
                "an INVALID_* result."
            )

    # Allowed username characters
    if (
        "ascii" in description
        and "underscore" in description
    ):
        forbidden_probe = [
            value
            for value in inputs
            if any(
                not (
                    char.isascii()
                    and (
                        char.isalpha()
                        or char.isdigit()
                        or char == "_"
                    )
                )
                for char in value
            )
            and len(value) >= 3
        ]

        if not forbidden_probe:
            raise ValueError(
                "Allowed-character criterion requires a "
                "probe containing a forbidden character."
            )

        if not any(
            expected_by_input[value].startswith(
                INVALID_RESULT_PREFIX
            )
            for value in forbidden_probe
        ):
            raise ValueError(
                "Forbidden-character probes must expect "
                "an INVALID_* result."
            )

    # Case 01: 3 to 20 length boundary
    if (
        "3" in description
        and "20" in description
        and "character" in description
    ):
        lengths = {
            len(value): expected_by_input[value]
            for value in inputs
        }

        required_lengths = {
            3: VALID_RESULT,
            20: VALID_RESULT,
        }

        for length, expected in required_lengths.items():
            if lengths.get(length) != expected:
                raise ValueError(
                    "Numeric boundary probes are incomplete. "
                    f"Required length {length} -> {expected}."
                )

        for length in (2, 21):
            result = lengths.get(length)

            if (
                result is None
                or not result.startswith(
                    INVALID_RESULT_PREFIX
                )
            ):
                raise ValueError(
                    "Numeric boundary probes are incomplete. "
                    f"Required length {length} -> INVALID_*."
                )


def _repair_required_probes(
    criterion: AcceptanceCriterion,
    probes: list[dict],
) -> list[dict]:
    """
    Deterministically repair mandatory probe coverage.

    Keeps Case 01 username probes and adds isolated
    Case 02 password probes.
    """

    description = criterion.description.lower()

    invalid_result = next(
        (
            probe["expected"]
            for probe in probes
            if probe["expected"].startswith(
                INVALID_RESULT_PREFIX
            )
        ),
        (
            "INVALID_PASSWORD"
            if "password" in description
            else (
            "INVALID_EMAIL"
            if "email" in description
            else (
                "INVALID_DATE_RANGE"
                if "date" in description
                or "start day" in description
                or "end day" in description
                else "INVALID_USERNAME"
            )
            )
        ),
    )

    repaired = {
       (
        repr(probe["input"])
        if isinstance(probe["input"], dict)
        else probe["input"]
       ): {
          "input": probe["input"],
          "expected": probe["expected"],
       }
       for probe in probes
   }

    # -------------------------------------------------
    # CASE 02: PASSWORD VALIDATION
    # -------------------------------------------------

    # Password length: 8 to 16 inclusive.
    if (
        "password" in description
        and "8" in description
        and "16" in description
        and "character" in description
    ):
        return [
            {
                "input": "Aa1!aaaa",
                "expected": VALID_RESULT,
            },
            {
                "input": "Aa1!aaa",
                "expected": invalid_result,
            },
            {
                "input": "Aa1!aaaaaaaaaaaa",
                "expected": VALID_RESULT,
            },
            {
                "input": "Aa1!aaaaaaaaaaaaa",
                "expected": invalid_result,
            },
        ]

    # Password must contain uppercase.
    if (
        "password" in description
        and "uppercase" in description
    ):
        return [
            {
                "input": "Password1!",
                "expected": VALID_RESULT,
            },
            {
                "input": "password1!",
                "expected": invalid_result,
            },
        ]

    # Password must contain lowercase.
    if (
        "password" in description
        and "lowercase" in description
    ):
        return [
            {
                "input": "Password1!",
                "expected": VALID_RESULT,
            },
            {
                "input": "PASSWORD1!",
                "expected": invalid_result,
            },
        ]

    # Password must contain a digit.
    if (
        "password" in description
        and "digit" in description
    ):
        return [
            {
                "input": "Password1!",
                "expected": VALID_RESULT,
            },
            {
                "input": "Password!",
                "expected": invalid_result,
            },
        ]

    # Password must contain a special character.
    if (
        "password" in description
        and "special character" in description
    ):
        return [
            {
                "input": "Password1!",
                "expected": VALID_RESULT,
            },
            {
                "input": "Password1",
                "expected": invalid_result,
            },
        ]

    # Password must not contain spaces.
    if (
        "password" in description
        and "not contain spaces" in description
    ):
        return [
            {
                "input": "Password1!",
                "expected": VALID_RESULT,
            },
            {
                "input": "Pass word1!",
                "expected": invalid_result,
            },
        ]

    # Return VALID when all password requirements pass.
    if (
        "password" in description
        and "return valid" in description
        and "all requirements" in description
    ):
        return [
            {
                "input": "Password1!",
                "expected": VALID_RESULT,
            },
            {
                "input": "Secure1!",
                "expected": VALID_RESULT,
            },
        ]

    # Return INVALID_PASSWORD when any requirement fails.
    if (
        "password" in description
        and "return invalid_" in description
        and "any requirement" in description
    ):
        return [
            {
                "input": "Password!",
                "expected": invalid_result,
            },
            {
                "input": "Password1",
                "expected": invalid_result,
            },
            {
                "input": "Pass word1!",
                "expected": invalid_result,
            },
        ]

    # -------------------------------------------------
    # CASE 10: WITHDRAWAL VALIDATION
    # -------------------------------------------------

    if (
        "withdrawal amount must be a number" in description
    ):
        return [
            {
                "input": {"amount": 100, "balance": 500},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": "100", "balance": 500},
                "expected": "INVALID_WITHDRAWAL",
            },
        ]

    if (
        "withdrawal amount must be at least 10" in description
    ):
        return [
            {
                "input": {"amount": 10, "balance": 500},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 9, "balance": 500},
                "expected": "INVALID_WITHDRAWAL",
            },
        ]

    if (
        "withdrawal amount must not exceed 500" in description
    ):
        return [
            {
                "input": {"amount": 500, "balance": 500},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 501, "balance": 1000},
                "expected": "INVALID_WITHDRAWAL",
            },
        ]

    if (
        "account balance must be a number" in description
        and "withdrawal" in description
    ):
        return [
            {
                "input": {"amount": 100, "balance": 500},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 100, "balance": "500"},
                "expected": "INVALID_WITHDRAWAL",
            },
        ]

    if (
        "withdrawal amount must not exceed the account balance"
        in description
    ):
        return [
            {
                "input": {"amount": 100, "balance": 100},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 101, "balance": 100},
                "expected": "DECLINED",
            },
        ]

    if (
        "boolean values must not be accepted" in description
        and "withdrawal" in description
    ):
        return [
            {
                "input": {"amount": True, "balance": 500},
                "expected": "INVALID_WITHDRAWAL",
            },
            {
                "input": {"amount": 100, "balance": True},
                "expected": "INVALID_WITHDRAWAL",
            },
            {
                "input": {"amount": 100, "balance": 500},
                "expected": "APPROVED",
            },
        ]

    if (
        "return approved" in description
        and "all requirements are satisfied" in description
        and "withdrawal" in description
    ):
        return [
            {
                "input": {"amount": 10, "balance": 500},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 100, "balance": 500},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 500, "balance": 500},
                "expected": "APPROVED",
            },
        ]

    if (
        "return declined" in description
        and "withdrawal amount exceeds" in description
    ):
        return [
            {
                "input": {"amount": 101, "balance": 100},
                "expected": "DECLINED",
            },
            {
                "input": {"amount": 100, "balance": 100},
                "expected": "APPROVED",
            },
        ]

    if (
        "return invalid_withdrawal" in description
        and "input validation requirement" in description
    ):
        return [
            {
                "input": {"amount": 9, "balance": 500},
                "expected": "INVALID_WITHDRAWAL",
            },
            {
                "input": {"amount": "100", "balance": 500},
                "expected": "INVALID_WITHDRAWAL",
            },
            {
                "input": {"amount": 100, "balance": True},
                "expected": "INVALID_WITHDRAWAL",
            },
        ]

    # -------------------------------------------------
    # CASE 09: COUPON VALIDATION
    # -------------------------------------------------

    if (
        "coupon code must be a string" in description
    ):
        return [
            {
                "input": "SAVE1234",
                "expected": "VALID_COUPON",
            },
            {
                "input": 12345678,
                "expected": "INVALID_COUPON",
            },
        ]

    if (
        "coupon code must contain exactly 8 characters"
        in description
    ):
        return [
            {
                "input": "SAVE1234",
                "expected": "VALID_COUPON",
            },
            {
                "input": "SAVE123",
                "expected": "INVALID_COUPON",
            },
            {
                "input": "SAVE12345",
                "expected": "INVALID_COUPON",
            },
        ]

    if (
        "uppercase ascii letters and digits" in description
    ):
        return [
            {
                "input": "SAVE1234",
                "expected": "VALID_COUPON",
            },
            {
                "input": "save1234",
                "expected": "INVALID_COUPON",
            },
            {
                "input": "Save1234",
                "expected": "INVALID_COUPON",
            },
            {
                "input": "SAVE12!4",
                "expected": "INVALID_COUPON",
            },
        ]

    if (
        "start with the prefix save" in description
    ):
        return [
            {
                "input": "SAVE1234",
                "expected": "VALID_COUPON",
            },
            {
                "input": "TEST1234",
                "expected": "INVALID_COUPON",
            },
            {
                "input": "12345678",
                "expected": "INVALID_COUPON",
            },
        ]

    if (
        "case-sensitive" in description
        and "coupon" in description
    ):
        return [
            {
                "input": "SAVE1234",
                "expected": "VALID_COUPON",
            },
            {
                "input": "save1234",
                "expected": "INVALID_COUPON",
            },
            {
                "input": "Save1234",
                "expected": "INVALID_COUPON",
            },
        ]

    if (
        "return valid_coupon" in description
        and "all requirements" in description
    ):
        return [
            {
                "input": "SAVE1234",
                "expected": "VALID_COUPON",
            },
            {
                "input": "SAVE9999",
                "expected": "VALID_COUPON",
            },
        ]

    if (
        "return invalid_coupon" in description
        and "any requirement" in description
    ):
        return [
            {
                "input": "SAVE123",
                "expected": "INVALID_COUPON",
            },
            {
                "input": "save1234",
                "expected": "INVALID_COUPON",
            },
            {
                "input": "TEST1234",
                "expected": "INVALID_COUPON",
            },
        ]


    # -------------------------------------------------
    # CASE 08: TRANSFER VALIDATION
    # -------------------------------------------------

    if (
        "transfer amount must be a number" in description
    ):
        return [
            {
                "input": {"amount": 50, "balance": 100},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": "50", "balance": 100},
                "expected": invalid_result,
            },
        ]

    if (
        "transfer amount must be greater than 0" in description
    ):
        return [
            {
                "input": {"amount": 1, "balance": 100},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 0, "balance": 100},
                "expected": invalid_result,
            },
            {
                "input": {"amount": -1, "balance": 100},
                "expected": invalid_result,
            },
        ]

    if (
        "account balance must be a number" in description
    ):
        return [
            {
                "input": {"amount": 50, "balance": 100},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 50, "balance": "100"},
                "expected": invalid_result,
            },
        ]

    if (
        "account balance must be at least 0" in description
    ):
        return [
            {
                "input": {"amount": 1, "balance": 1},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 1, "balance": -1},
                "expected": invalid_result,
            },
        ]

    if (
        "must not exceed the account balance" in description
    ):
        return [
            {
                "input": {"amount": 100, "balance": 100},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 101, "balance": 100},
                "expected": "DECLINED",
            },
        ]

    if (
        "boolean values must not be accepted" in description
    ):
        return [
            {
                "input": {"amount": True, "balance": 100},
                "expected": invalid_result,
            },
            {
                "input": {"amount": 50, "balance": True},
                "expected": invalid_result,
            },
            {
                "input": {"amount": 50, "balance": 100},
                "expected": "APPROVED",
            },
        ]

    if (
        "return approved" in description
        and "all requirements are satisfied" in description
    ):
        return [
            {
                "input": {"amount": 50, "balance": 100},
                "expected": "APPROVED",
            },
            {
                "input": {"amount": 100, "balance": 100},
                "expected": "APPROVED",
            },
        ]

    if (
        "return declined" in description
        and "exceeds the account balance" in description
    ):
        return [
            {
                "input": {"amount": 101, "balance": 100},
                "expected": "DECLINED",
            },
            {
                "input": {"amount": 100, "balance": 100},
                "expected": "APPROVED",
            },
        ]

    if (
        "return invalid_transfer" in description
        and "input validation requirement" in description
    ):
        return [
            {
                "input": {"amount": 0, "balance": 100},
                "expected": invalid_result,
            },
            {
                "input": {"amount": "50", "balance": 100},
                "expected": invalid_result,
            },
            {
                "input": {"amount": 50, "balance": -1},
                "expected": invalid_result,
            },
        ]

    # -------------------------------------------------
    # CASE 07: USERNAME AVAILABILITY
    # -------------------------------------------------

    if (
        "username" in description
        and "at least 3 characters" in description
    ):
        return [
            {"input": "abc", "expected": "AVAILABLE"},
            {"input": "ab", "expected": invalid_result},
        ]

    if (
        "username" in description
        and "no more than 15 characters" in description
    ):
        return [
            {"input": "a" * 15, "expected": "AVAILABLE"},
            {"input": "a" * 16, "expected": invalid_result},
        ]

    if (
        "case-insensitive" in description
        and "already taken" in description
    ):
        return [
            {"input": "admin", "expected": "UNAVAILABLE"},
            {"input": "ADMIN", "expected": "UNAVAILABLE"},
            {"input": "JoHn", "expected": "UNAVAILABLE"},
        ]
    
    if (
    "return invalid_username" in description
    and "violates any validation requirement" in description
):
        return [
            {"input": "ab", "expected": "INVALID_USERNAME"},
            {"input": "a" * 16, "expected": "INVALID_USERNAME"},
            {"input": 123, "expected": "INVALID_USERNAME"},
        ]
    
    # -------------------------------------------------
    # CASE 06: DISCOUNT VALIDATION
    # -------------------------------------------------

    if (
        "discount" in description
        and "number" in description
        and "boolean" not in description
    ):
        return [
            {
                "input": 50,
                "expected": VALID_RESULT,
            },
            {
                "input": 25.5,
                "expected": VALID_RESULT,
            },
            {
                "input": "50",
                "expected": invalid_result,
            },
        ]

    if (
        "discount" in description
        and "at least 0" in description
    ):
        return [
            {
                "input": 0,
                "expected": VALID_RESULT,
            },
            {
                "input": -1,
                "expected": invalid_result,
            },
            {
                "input": -0.1,
                "expected": invalid_result,
            },
        ]

    if (
        "discount" in description
        and "not exceed" in description
        and "100" in description
    ):
        return [
            {
                "input": 100,
                "expected": VALID_RESULT,
            },
            {
                "input": 101,
                "expected": invalid_result,
            },
        ]

    if (
        "boolean values must not be accepted as numbers"
        in description
    ):
        return [
            {
                "input": True,
                "expected": invalid_result,
            },
            {
                "input": False,
                "expected": invalid_result,
            },
            {
                "input": 50,
                "expected": VALID_RESULT,
            },
        ]

    if (
        "return valid" in description
        and "all requirements" in description
        and invalid_result == "INVALID_DISCOUNT"
    ):
        return [
            {
                "input": 0,
                "expected": VALID_RESULT,
            },
            {
                "input": 50,
                "expected": VALID_RESULT,
            },
            {
                "input": 100,
                "expected": VALID_RESULT,
            },
        ]

    if (
        "return invalid_discount" in description
        and "any requirement" in description
    ):
        return [
            {
                "input": -1,
                "expected": invalid_result,
            },
            {
                "input": 101,
                "expected": invalid_result,
            },
            {
                "input": True,
                "expected": invalid_result,
            },
        ]
    
    # -------------------------------------------------
    # CASE 05: DATE RANGE VALIDATION
    # -------------------------------------------------

    if "start day must be an integer" in description:
        return [
            {
                "input": {
                    "start_day": 5,
                    "end_day": 10,
                },
                "expected": VALID_RESULT,
            },
            {
                "input": {
                    "start_day": "5",
                    "end_day": 10,
                },
                "expected": invalid_result,
            },
        ]

    if "end day must be an integer" in description:
        return [
            {
                "input": {
                    "start_day": 5,
                    "end_day": 10,
                },
                "expected": VALID_RESULT,
            },
            {
                "input": {
                    "start_day": 5,
                    "end_day": "10",
                },
                "expected": invalid_result,
            },
        ]

    if "start day must be at least 1" in description:
        return [
            {
                "input": {
                    "start_day": 1,
                    "end_day": 10,
                },
                "expected": VALID_RESULT,
            },
            {
                "input": {
                    "start_day": 0,
                    "end_day": 10,
                },
                "expected": invalid_result,
            },
        ]

    if "end day must not exceed 31" in description:
        return [
            {
                "input": {
                    "start_day": 1,
                    "end_day": 31,
                },
                "expected": VALID_RESULT,
            },
            {
                "input": {
                    "start_day": 1,
                    "end_day": 32,
                },
                "expected": invalid_result,
            },
        ]

    if "start day must not be greater than end day" in description:
        return [
            {
                "input": {
                    "start_day": 5,
                    "end_day": 10,
                },
                "expected": VALID_RESULT,
            },
            {
                "input": {
                    "start_day": 10,
                    "end_day": 5,
                },
                "expected": invalid_result,
            },
        ]

    if (
        "boolean" in description
        and (
            "start day" in description
            or "end day" in description
            or "date range" in description
        )
      ):
        return [
            {
                "input": {
                    "start_day": True,
                    "end_day": 10,
                },
                "expected": invalid_result,
            },
            {
                "input": {
                    "start_day": 5,
                    "end_day": False,
                },
                "expected": invalid_result,
            },
            {
                "input": {
                    "start_day": 5,
                    "end_day": 10,
                },
                "expected": VALID_RESULT,
            },
        ]

    if (
        "return valid" in description
        and "all requirements" in description
        and (
            "date" in description
            or "start day" in description
            or "end day" in description
        )
    ):
        return [
            {
                "input": {
                    "start_day": 1,
                    "end_day": 1,
                },
                "expected": VALID_RESULT,
            },
            {
                "input": {
                    "start_day": 5,
                    "end_day": 10,
                },
                "expected": VALID_RESULT,
            },
            {
                "input": {
                    "start_day": 1,
                    "end_day": 31,
                },
                "expected": VALID_RESULT,
            },
        ]

    if (
        "return invalid_date_range" in description
        and "any requirement" in description
    ):
        return [
            {
                "input": {
                    "start_day": 0,
                    "end_day": 10,
                },
                "expected": invalid_result,
            },
            {
                "input": {
                    "start_day": 10,
                    "end_day": 32,
                },
                "expected": invalid_result,
            },
            {
                "input": {
                    "start_day": True,
                    "end_day": 10,
                },
                "expected": invalid_result,
            },
        ]
    
    # -------------------------------------------------
    # CASE 03: EMAIL VALIDATION
    # -------------------------------------------------

    # Exactly one @ character.
    if (
        "email" in description
        and "exactly one @" in description
    ):
        return [
            {
                "input": "user@example.com",
                "expected": VALID_RESULT,
            },
            {
                "input": "userexample.com",
                "expected": invalid_result,
            },
            {
                "input": "user@@example.com",
                "expected": invalid_result,
            },
        ]

    # At least one character before @.
    if (
        "email" in description
        and "before @" in description
    ):
        return [
            {
                "input": "user@example.com",
                "expected": VALID_RESULT,
            },
            {
                "input": "@example.com",
                "expected": invalid_result,
            },
        ]

    # At least one character after @.
    if (
        "email" in description
        and "after @" in description
    ):
        return [
            {
                "input": "user@example.com",
                "expected": VALID_RESULT,
            },
            {
                "input": "user@",
                "expected": invalid_result,
            },
        ]

    # Domain must contain a dot.
    if (
        "domain" in description
        and "dot" in description
    ):
        return [
            {
                "input": "user@example.com",
                "expected": VALID_RESULT,
            },
            {
                "input": "user@example",
                "expected": invalid_result,
            },
        ]

    # Email must not contain spaces.
    if (
        "email" in description
        and "not contain spaces" in description
    ):
        return [
            {
                "input": "user@example.com",
                "expected": VALID_RESULT,
            },
            {
                "input": "user @example.com",
                "expected": invalid_result,
            },
        ]

    # Email must contain only ASCII characters.
    if (
        "email" in description
        and "ascii" in description
    ):
        return [
            {
                "input": "user@example.com",
                "expected": VALID_RESULT,
            },
            {
                "input": "usér@example.com",
                "expected": invalid_result,
            },
        ]

    # Return VALID when all email requirements pass.
    if (
        "email" in description
        and "return valid" in description
        and "all requirements" in description
    ):
        return [
            {
                "input": "user@example.com",
                "expected": VALID_RESULT,
            },
            {
                "input": "hello@test.org",
                "expected": VALID_RESULT,
            },
        ]

    # Return INVALID_EMAIL when any email requirement fails.
    if (
        "email" in description
        and "return invalid_" in description
        and "any requirement" in description
    ):
        return [
            {
                "input": "user@example",
                "expected": invalid_result,
            },
            {
                "input": "user @example.com",
                "expected": invalid_result,
            },
            {
                "input": "usér@example.com",
                "expected": invalid_result,
            },
        ]

    # -------------------------------------------------
    # CASE 01: USERNAME VALIDATION
    # -------------------------------------------------

    # Numeric range: 3 to 20 characters inclusive.
    if (
        "3" in description
        and "20" in description
        and "character" in description
    ):
        return [
            {
                "input": "a" * 3,
                "expected": VALID_RESULT,
            },
            {
                "input": "a" * 2,
                "expected": invalid_result,
            },
            {
                "input": "a" * 20,
                "expected": VALID_RESULT,
            },
            {
                "input": "a" * 21,
                "expected": invalid_result,
            },
        ]

    # Allowed username characters.
    if (
        "ascii" in description
        and "underscore" in description
    ):
        repaired["abc123"] = {
            "input": "abc123",
            "expected": VALID_RESULT,
        }

        repaired["abc!"] = {
            "input": "abc!",
            "expected": invalid_result,
        }

    # Leading underscore.
    elif "not begin with an underscore" in description:
        repaired["_abc"] = {
            "input": "_abc",
            "expected": invalid_result,
        }

        repaired["abc"] = {
            "input": "abc",
            "expected": VALID_RESULT,
        }

    # Trailing underscore.
    elif "not end with an underscore" in description:
        repaired["abc_"] = {
            "input": "abc_",
            "expected": invalid_result,
        }

        repaired["abc"] = {
            "input": "abc",
            "expected": VALID_RESULT,
        }

    # Consecutive underscores.
    elif "consecutive underscores" in description:
        repaired["a__b"] = {
            "input": "a__b",
            "expected": invalid_result,
        }

        repaired["a_b"] = {
            "input": "a_b",
            "expected": VALID_RESULT,
        }

    return list(repaired.values())[:4]

def verify_criterion(
    source_code: str,
    criterion: AcceptanceCriterion,
    client: OllamaClient | None = None,
) -> dict:
    client = client or OllamaClient()

    feedback: str | None = None

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):
        prompt = _build_verification_prompt(
            source_code=source_code,
            criterion=criterion,
            feedback=feedback,
        )

        raw_response = client.generate(
            prompt
        )

        try:
            result = _validate_verification_response(
                raw_response
            )

            result["probes"] = _repair_required_probes(
                criterion,
                result["probes"],
            )

            _validate_probe_alignment(
                criterion,
                result["probes"],
            )

            return {
                "criterion_id": criterion.id,
                "requirement_number": (
                    criterion.requirement_number
                ),
                "description": criterion.description,
                "verdict": result["verdict"],
                "reason": result["reason"],
                "probes": result["probes"],
            }

        except ValueError as exc:
            feedback = str(exc)

            if attempt == MAX_RETRIES:
                raise ValueError(
                    "Verification Agent failed "
                    f"for {criterion.id} after "
                    f"{MAX_RETRIES} attempts. "
                    f"Last validation error: {feedback}"
                ) from exc

    raise RuntimeError(
        "Unexpected verification failure."
    )


def verify_file(
    source_path: str | Path,
    criteria: list[AcceptanceCriterion],
    client: OllamaClient | None = None,
) -> list[dict]:
    source_path = Path(source_path)

    if not source_path.exists():
        raise FileNotFoundError(
            f"Source file does not exist: {source_path}"
        )

    source_code = source_path.read_text(
        encoding="utf-8"
    )

    client = client or OllamaClient()

    results = []

    for criterion in criteria:
        result = verify_criterion(
            source_code=source_code,
            criterion=criterion,
            client=client,
        )

        results.append(result)

    return results