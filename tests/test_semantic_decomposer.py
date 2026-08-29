from specguard.parser import parse_requirement_file
from specguard.semantic_decomposer import semantic_decompose


class FakeOllamaClient:
    """
    Deterministic fake LLM for unit testing.

    It identifies the actual requirement using the final
    'Requirement:' section of the prompt.
    """

    def generate(self, prompt: str) -> str:
        requirement_text = (
            prompt.rsplit("Requirement:", 1)[-1]
            .strip()
            .lower()
        )

        if "between 3 and 20" in requirement_text:
            return """
            {
              "criteria": [
                {
                  "description":
                  "Username must be between 3 and 20 characters inclusive."
                }
              ]
            }
            """

        if "ascii letters" in requirement_text:
            return """
            {
              "criteria": [
                {
                  "description":
                  "Username must contain only ASCII letters, digits, or underscore."
                }
              ]
            }
            """

        if "begin or end" in requirement_text:
            return """
            {
              "criteria": [
                {
                  "description":
                  "Username must not begin with an underscore."
                },
                {
                  "description":
                  "Username must not end with an underscore."
                }
              ]
            }
            """

        if "consecutive underscores" in requirement_text:
            return """
            {
              "criteria": [
                {
                  "description":
                  "Username must not contain consecutive underscores."
                }
              ]
            }
            """

        if "invalid_username" in requirement_text:
            return """
            {
              "criteria": [
                {
                  "description":
                  "Return INVALID_USERNAME when any requirement is violated."
                }
              ]
            }
            """

        if "valid" in requirement_text:
            return """
            {
              "criteria": [
                {
                  "description":
                  "Return VALID when all requirements are satisfied."
                }
              ]
            }
            """

        raise AssertionError(
            f"Unexpected requirement:\n{requirement_text}"
        )


def test_semantic_decompose_case_01():
    specification = parse_requirement_file(
        "evaluation/cases/case_01/requirement.md"
    )

    criteria = semantic_decompose(
        specification,
        client=FakeOllamaClient(),
    )

    assert len(criteria) == 7

    assert [
        criterion.requirement_number
        for criterion in criteria
    ] == [1, 2, 3, 3, 4, 5, 6]

    assert criteria[0].description == (
        "Username must be between 3 and 20 characters inclusive."
    )

    assert criteria[2].description == (
        "Username must not begin with an underscore."
    )

    assert criteria[3].description == (
        "Username must not end with an underscore."
    )

    assert criteria[2].id == "AC-03"
    assert criteria[3].id == "AC-04"

    assert all(
        criterion.category == "semantic"
        for criterion in criteria
    )