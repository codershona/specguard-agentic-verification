import json
from pathlib import Path

from specguard.decomposer import AcceptanceCriterion
from specguard.llm import OllamaClient


MAX_RETRIES = 3


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

Every probe MUST contain exactly these two fields:
- "input"
- "expected"

"expected" MUST always be either:
- "VALID"
- "INVALID_USERNAME"

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
      "expected": "expected result"
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

        # Accept a few common model variations.
        test_input = (
            probe.get("input")
            or probe.get("test_input")
            or probe.get("value")
        )

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

        if not isinstance(test_input, str):
            test_input = str(test_input)

        if not isinstance(expected, str):
            expected = str(expected)

        expected = expected.strip()

        if expected not in {
            "VALID",
            "INVALID_USERNAME",
        }:
            raise ValueError(
                f"Probe {index} has invalid expected "
                f"value {expected!r}. "
                "Expected must be VALID or "
                "INVALID_USERNAME."
            )

        signature = (
            test_input,
            expected,
        )

        if signature in seen:
            raise ValueError(
                "Duplicate probes are not allowed."
            )

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
        probe["input"]: probe["expected"]
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
                "valid-length probe beginning with '_'. "
                "Example: '_abc' -> INVALID_USERNAME."
            )

        if not any(
            expected_by_input[value]
            == "INVALID_USERNAME"
            for value in violating
        ):
            raise ValueError(
                "A leading-underscore probe must expect "
                "INVALID_USERNAME."
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
                "valid-length probe ending with '_'. "
                "Example: 'abc_' -> INVALID_USERNAME."
            )

        if not any(
            expected_by_input[value]
            == "INVALID_USERNAME"
            for value in violating
        ):
            raise ValueError(
                "A trailing-underscore probe must expect "
                "INVALID_USERNAME."
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
                "a probe containing '__'. "
                "Example: 'a__b' -> INVALID_USERNAME."
            )

        if not any(
            expected_by_input[value]
            == "INVALID_USERNAME"
            for value in violating
        ):
            raise ValueError(
                "A probe containing consecutive underscores "
                "must expect INVALID_USERNAME."
            )

    # Allowed characters
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
                "valid-length probe containing a forbidden "
                "character, such as 'abc!'."
            )

        if not any(
            expected_by_input[value]
            == "INVALID_USERNAME"
            for value in forbidden_probe
        ):
            raise ValueError(
                "Forbidden-character probes must expect "
                "INVALID_USERNAME."
            )

    # 3 to 20 length boundary
    if (
        "3" in description
        and "20" in description
        and "character" in description
    ):
        lengths = {
            len(value): expected_by_input[value]
            for value in inputs
        }

        required = {
            3: "VALID",
            2: "INVALID_USERNAME",
            20: "VALID",
            21: "INVALID_USERNAME",
        }

        missing = []

        for length, expected in required.items():
            if (
                length not in lengths
                or lengths[length] != expected
            ):
                missing.append(
                    f"length {length} -> {expected}"
                )

        if missing:
            raise ValueError(
                "Numeric boundary probes are incomplete. "
                "Required: "
                + ", ".join(missing)
            )


def _repair_required_probes(
    criterion: AcceptanceCriterion,
    probes: list[dict],
) -> list[dict]:
    """
    Deterministically repair mandatory probe coverage.
    """

    description = criterion.description.lower()

    repaired = {
        probe["input"]: {
            "input": probe["input"],
            "expected": probe["expected"],
        }
        for probe in probes
    }

    # Numeric range: 3 to 20 characters inclusive.
    if (
        "3" in description
        and "20" in description
        and "character" in description
    ):
        repaired = {
            "a" * 3: {
                "input": "a" * 3,
                "expected": "VALID",
            },
            "a" * 2: {
                "input": "a" * 2,
                "expected": "INVALID_USERNAME",
            },
            "a" * 20: {
                "input": "a" * 20,
                "expected": "VALID",
            },
            "a" * 21: {
                "input": "a" * 21,
                "expected": "INVALID_USERNAME",
            },
        }

    # Allowed characters.
    elif (
        "ascii" in description
        and "underscore" in description
    ):
        repaired["abc123"] = {
            "input": "abc123",
            "expected": "VALID",
        }
        repaired["abc!"] = {
            "input": "abc!",
            "expected": "INVALID_USERNAME",
        }

    # Leading underscore.
    elif "not begin with an underscore" in description:
        repaired["_abc"] = {
            "input": "_abc",
            "expected": "INVALID_USERNAME",
        }
        repaired["abc"] = {
            "input": "abc",
            "expected": "VALID",
        }

    # Trailing underscore.
    elif "not end with an underscore" in description:
        repaired["abc_"] = {
            "input": "abc_",
            "expected": "INVALID_USERNAME",
        }
        repaired["abc"] = {
            "input": "abc",
            "expected": "VALID",
        }

    # Consecutive underscores.
    elif "consecutive underscores" in description:
        repaired["a__b"] = {
            "input": "a__b",
            "expected": "INVALID_USERNAME",
        }
        repaired["a_b"] = {
            "input": "a_b",
            "expected": "VALID",
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