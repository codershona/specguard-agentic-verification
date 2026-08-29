import json

from specguard.decomposer import AcceptanceCriterion
from specguard.llm import OllamaClient
from specguard.models import Specification


MAX_RETRIES = 3


def _build_prompt(
    requirement_text: str,
    feedback: str | None = None,
) -> str:
    prompt = f"""
You are SpecGuard's Requirement Reasoning Agent.

Decompose ONE software requirement into the smallest set of
independently testable acceptance criteria.

IMPORTANT:
Do NOT split a requirement merely because it contains multiple
values, boundaries, examples, or allowed options.

Split ONLY when the requirement contains separate conditions that
can independently pass or fail.

Rules:

1. Preserve the exact meaning of the original requirement.
2. Do not invent, weaken, strengthen, or duplicate requirements.
3. Do not change numeric boundaries.
4. Do not split a numeric range into multiple criteria.
5. Do not split a list of allowed values into multiple criteria.
6. Do not create duplicate criteria.
7. Split only genuinely independent conditions.
8. Return only valid JSON.
9. Do not include markdown or explanations.

Examples:

INPUT:
Username must be between 3 and 20 characters inclusive.

CORRECT:
Username must be between 3 and 20 characters inclusive.

WRONG:
Be between 3 and 19 characters inclusive.
Be between 19 and 20 characters inclusive.

INPUT:
Username may contain only ASCII letters, digits, or underscore.

CORRECT:
Username may contain only ASCII letters, digits, or underscore.

Do NOT create separate criteria for letters, digits, and underscore.

INPUT:
Username must not begin or end with an underscore.

CORRECT:
Username must not begin with an underscore.
Username must not end with an underscore.

This is split because beginning and ending are independently
testable conditions.

Return exactly:

{{
  "criteria": [
    {{
      "description": "criterion text"
    }}
  ]
}}

Requirement:
{requirement_text}
"""

    if feedback:
        prompt += f"""

Your previous response failed validation.

Problem:
{feedback}

Generate the complete corrected JSON response again.
"""

    return prompt


def _validate_response(
    raw_response: str,
) -> list[str]:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Response is not valid JSON."
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(
            "Response must be a JSON object."
        )

    criteria = parsed.get("criteria")

    if not isinstance(criteria, list):
        raise ValueError(
            "'criteria' must be a list."
        )

    if not criteria:
        raise ValueError(
            "'criteria' cannot be empty."
        )

    descriptions: list[str] = []

    for index, item in enumerate(criteria, start=1):
        if not isinstance(item, dict):
            raise ValueError(
                f"Criterion {index} must be an object."
            )

        description = item.get("description")

        if not isinstance(description, str):
            raise ValueError(
                f"Criterion {index} must contain "
                "a string 'description'."
            )

        description = description.strip()

        if not description:
            raise ValueError(
                f"Criterion {index} has an empty description."
            )

        descriptions.append(description)

    # Prevent exact duplicates.
    normalized = [
        description.lower().strip()
        for description in descriptions
    ]

    if len(normalized) != len(set(normalized)):
        raise ValueError(
            "Response contains duplicate acceptance criteria."
        )

    return descriptions


def _validate_atomicity(
    descriptions: list[str],
) -> None:
    """
    Reject obvious cases where an independently testable compound
    condition was not decomposed.
    """

    for index, description in enumerate(
        descriptions,
        start=1,
    ):
        normalized = description.lower()

        if "begin or end" in normalized:
            raise ValueError(
                f"Criterion {index} still contains "
                "'begin or end'. Split beginning and ending "
                "into separate criteria."
            )

        if "start or end" in normalized:
            raise ValueError(
                f"Criterion {index} still contains "
                "'start or end'. Split starting and ending "
                "into separate criteria."
            )


def _decompose_single_requirement(
    client: OllamaClient,
    requirement_number: int,
    requirement_text: str,
) -> list[str]:
    feedback: str | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        prompt = _build_prompt(
            requirement_text=requirement_text,
            feedback=feedback,
        )

        raw_response = client.generate(prompt)

        try:
            descriptions = _validate_response(
                raw_response
            )

            _validate_atomicity(descriptions)

            return descriptions

        except ValueError as exc:
            feedback = str(exc)

            if attempt == MAX_RETRIES:
                raise ValueError(
                    "Requirement Reasoning Agent failed "
                    f"for requirement {requirement_number} "
                    f"after {MAX_RETRIES} attempts. "
                    f"Last error: {feedback}"
                ) from exc

    raise RuntimeError(
        "Unexpected requirement decomposition failure."
    )


def semantic_decompose(
    specification: Specification,
    client: OllamaClient | None = None,
) -> list[AcceptanceCriterion]:
    """
    Semantically decompose requirements into independently
    verifiable acceptance criteria.

    The LLM performs semantic reasoning only.

    Requirement numbers and criterion IDs are assigned
    deterministically by SpecGuard to preserve traceability.
    """

    client = client or OllamaClient()

    criteria: list[AcceptanceCriterion] = []

    criterion_index = 1

    for requirement in specification.requirements:
        requirement_number = int(
            requirement.metadata["number"]
        )

        descriptions = _decompose_single_requirement(
            client=client,
            requirement_number=requirement_number,
            requirement_text=requirement.text,
        )

        for description in descriptions:
            criterion = AcceptanceCriterion(
                id=f"AC-{criterion_index:02d}",
                requirement_number=requirement_number,
                description=description,
                category="semantic",
            )

            criteria.append(criterion)

            criterion_index += 1

    return criteria