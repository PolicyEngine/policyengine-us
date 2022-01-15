import pytest
from openfisca_us import CountryTaxBenefitSystem
from openfisca_core.simulation_builder import SimulationBuilder

system = CountryTaxBenefitSystem()
builder = SimulationBuilder()

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
    "initial_tanf_eligibility",
    "continuous_tanf_eligibility",
    "is_tanf_eligible",
)


@pytest.mark.parametrize("variable", system.variables)
def test_variable(variable: str) -> None:
    if variable not in EXEMPTIONS:
        simulation = builder.build_from_dict(system, DEFAULT_SITUATION)
        simulation.calculate(variable, 2022)
