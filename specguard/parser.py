import re
from pathlib import Path

from specguard.models import Requirement, Specification


NUMBERED_REQUIREMENT_PATTERN = re.compile(r"^\s*(\d+)\.\s+(.*)$")


def parse_requirement_file(path: str | Path) -> Specification:
    """
    Parse numbered requirements from a markdown requirement file.

    Only numbered statements inside the requirement section are treated
    as atomic requirements.
    """

    path = Path(path)
    specification = Specification()

    content = path.read_text(encoding="utf-8")

    for line in content.splitlines():
        match = NUMBERED_REQUIREMENT_PATTERN.match(line)

        if not match:
            continue

        number, text = match.groups()

        specification.add_requirement(
            Requirement(
                text=text.strip(),
                source=str(path),
                metadata={"number": int(number)},
            )
        )

    return specification