"""Check the legal-day boundary that monthly policy YAML cannot express."""

from pathlib import Path

from policyengine_core.parameters import load_parameter_file


def test_heat_and_eat_requirement_takes_effect_on_enactment_date():
    requirement = load_parameter_file(
        str(
            Path(__file__).resolve().parents[2]
            / "parameters/gov/usda/snap/income/deductions/utility"
            / "heat_and_eat_requires_elderly_disabled.yaml"
        )
    )
    assert requirement("2025-07-03") is False
    assert requirement("2025-07-04") is True
