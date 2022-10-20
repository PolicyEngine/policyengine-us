import pytest
from policyengine_us import CountryTaxBenefitSystem
from policyengine_core.simulations import SimulationBuilder

DEFAULT_SITUATION = {
    "people": {"person": {}},
    "tax_units": {"tax_unit": {"members": ["person"]}},
    "families": {"family": {"members": ["person"]}},
    "spm_units": {"spm_units": {"members": ["person"]}},
    "households": {"household": {"members": ["person"]}},
}

EXEMPTIONS = (
    "tanf_max_amount",
    "tanf",
    "tanf_amount_if_eligible",
    "tanf_countable_income",
    "tanf_initial_employment_deduction",
    "is_tanf_initial_eligible",
    "is_tanf_continuous_eligible",
    "is_tanf_eligible",
)


system = CountryTaxBenefitSystem()

simulation = SimulationBuilder().build_from_dict(system, DEFAULT_SITUATION)


@pytest.mark.parametrize("variable", system.variables)
def test_variable(variable: str) -> None:
    if variable not in EXEMPTIONS:
        simulation.calculate(variable, 2022)
