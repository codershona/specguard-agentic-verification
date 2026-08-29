from specguard.decomposer import decompose_specification
from specguard.parser import parse_requirement_file


def test_decompose_case_01():
    specification = parse_requirement_file(
        "evaluation/cases/case_01/requirement.md"
    )

    criteria = decompose_specification(specification)

    assert len(criteria) == 6

    assert criteria[0].id == "AC-01"
    assert criteria[0].requirement_number == 1
    assert criteria[0].description == (
        "Be between 3 and 20 characters inclusive."
    )

    assert criteria[-1].id == "AC-06"
    assert criteria[-1].requirement_number == 6