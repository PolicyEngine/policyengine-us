import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation


SYSTEM = CountryTaxBenefitSystem()


def make_simulation(
    period: str,
    *,
    enrolled: bool,
    meets_work_requirements: bool,
) -> Simulation:
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {period: 30},
                }
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": {period: "DC"},
                }
            },
            "spm_units": {
                "spm_unit": {
                    "members": ["person"],
                    "dc_tanf_eligible": {period: True},
                    "dc_tanf_standard_payment": {period: 100},
                    "dc_tanf_countable_income": {period: 0},
                    "dc_tanf_meets_work_requirements": {
                        period: meets_work_requirements
                    },
                    "is_tanf_enrolled": {period: enrolled},
                }
            },
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )


@pytest.mark.parametrize(
    (
        "period",
        "enrolled",
        "meets_work_requirements",
        "expected_rate",
        "expected_benefit",
    ),
    [
        ("2023-01", True, False, 0.06, 94),
        ("2023-01", False, False, 0, 100),
    ],
)
def test_dc_tanf_work_sanction_rate_and_benefit(
    period: str,
    enrolled: bool,
    meets_work_requirements: bool,
    expected_rate: float,
    expected_benefit: float,
):
    sim = make_simulation(
        period,
        enrolled=enrolled,
        meets_work_requirements=meets_work_requirements,
    )

    assert sim.calculate("dc_tanf_work_sanction_rate", period)[0] == pytest.approx(
        expected_rate
    )
    assert sim.calculate("dc_tanf", period)[0] == pytest.approx(expected_benefit)


def test_dc_tanf_work_sanction_rate_parameter_schedule():
    assert (
        SYSTEM.parameters(
            "2026-10"
        ).gov.states.dc.dhs.tanf.work_requirement.sanction.rate
    ) == pytest.approx(0.25)
