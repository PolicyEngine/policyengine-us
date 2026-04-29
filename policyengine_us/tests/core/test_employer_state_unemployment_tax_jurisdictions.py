import pytest

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.variables.gov.states.tax.payroll.unemployment._jurisdictions import (
    STATE_UNEMPLOYMENT_TAX_JURISDICTIONS,
)


SYSTEM = CountryTaxBenefitSystem()
PERIOD = "2026"


def make_simulation(state_code: str) -> Simulation:
    return Simulation(
        tax_benefit_system=SYSTEM,
        situation={
            "people": {
                "person": {
                    "age": {PERIOD: 30},
                    "employment_income": {PERIOD: 1_000},
                }
            },
            "households": {
                "household": {
                    "members": ["person"],
                    "state_code": {PERIOD: state_code},
                }
            },
            "tax_units": {"tax_unit": {"members": ["person"]}},
            "spm_units": {"spm_unit": {"members": ["person"]}},
            "families": {"family": {"members": ["person"]}},
            "marital_units": {"marital_unit": {"members": ["person"]}},
        },
    )


@pytest.mark.parametrize(
    ("state_code", "slug"),
    [
        (state_code, slug)
        for _, state_code, slug in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS
    ],
    ids=[state_code for _, state_code, _ in STATE_UNEMPLOYMENT_TAX_JURISDICTIONS],
)
def test_jurisdiction_specific_employer_state_unemployment_tax_formula(
    state_code: str, slug: str
):
    sim = make_simulation(state_code)

    expected = (
        sim.calculate("employer_state_unemployment_tax_rate", PERIOD)[0]
        * sim.calculate("taxable_earnings_for_state_unemployment_tax", PERIOD)[0]
    )
    jurisdiction_tax = sim.calculate(f"{slug}_employer_state_unemployment_tax", PERIOD)[
        0
    ]
    aggregate_tax = sim.calculate("employer_state_unemployment_tax", PERIOD)[0]

    assert jurisdiction_tax == pytest.approx(expected)
    assert aggregate_tax == pytest.approx(jurisdiction_tax)
