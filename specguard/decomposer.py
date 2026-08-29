from dataclasses import dataclass

from specguard.models import Requirement, Specification


@dataclass
class AcceptanceCriterion:
    id: str
    requirement_number: int
    description: str
    category: str


def decompose_specification(
    specification: Specification,
) -> list[AcceptanceCriterion]:
    """
    Convert requirements into atomic acceptance criteria.

    This is Iteration 1. It intentionally uses deterministic logic
    before we introduce an LLM-based reasoning agent.
    """

    criteria: list[AcceptanceCriterion] = []

    for requirement in specification.requirements:
        number = requirement.metadata["number"]

        criteria.append(
            AcceptanceCriterion(
                id=f"AC-{number:02d}",
                requirement_number=number,
                description=requirement.text,
                category="requirement",
            )
        )

    return criteria