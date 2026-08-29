from specguard.parser import parse_requirement_file


def test_parse_case_01_requirements():
    specification = parse_requirement_file(
        "evaluation/cases/case_01/requirement.md"
    )

    assert len(specification) == 6

    assert specification.requirements[0].text == (
        "Be between 3 and 20 characters inclusive."
    )

    assert specification.requirements[0].metadata["number"] == 1

    assert specification.requirements[-1].text == (
        "Return `INVALID_USERNAME` when any requirement is violated."
    )

    assert specification.requirements[-1].metadata["number"] == 6