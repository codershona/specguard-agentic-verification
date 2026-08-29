from dataclasses import dataclass, field


@dataclass
class Requirement:
    """A single requirement extracted from a specification."""

    text: str
    source: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Specification:
    """Structured representation of a parsed specification."""

    requirements: list[Requirement] = field(default_factory=list)

    def add_requirement(self, requirement: Requirement) -> None:
        self.requirements.append(requirement)

    def __len__(self) -> int:
        return len(self.requirements)