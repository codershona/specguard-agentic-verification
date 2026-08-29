from specguard.decomposer import AcceptanceCriterion
from specguard.verifier import verify_criterion


class FakeVerifierClient:
    def generate(self, prompt: str) -> str:
        return """
        {
          "verdict": "violated",
          "reason": "Leading underscore is not checked.",
          "probes": [
            {
              "input": "_alice",
              "expected": "INVALID_USERNAME"
            },
            {
              "input": "alice",
              "expected": "VALID"
            }
          ]
        }
        """


def test_verify_criterion_generates_multiple_probes():
    criterion = AcceptanceCriterion(
        id="AC-03",
        requirement_number=3,
        description=(
            "Username must not begin with an underscore."
        ),
        category="semantic",
    )

    source_code = """
def validate_username(username):
    return "VALID"
"""

    result = verify_criterion(
        source_code=source_code,
        criterion=criterion,
        client=FakeVerifierClient(),
    )

    assert result["criterion_id"] == "AC-03"
    assert result["requirement_number"] == 3
    assert result["verdict"] == "violated"

    assert len(result["probes"]) >= 2
    assert len(result["probes"]) <= 4

    probe_map = {
        probe["input"]: probe["expected"]
        for probe in result["probes"]
    }

    assert probe_map["_abc"] == "INVALID_USERNAME"
    assert probe_map["abc"] == "VALID"