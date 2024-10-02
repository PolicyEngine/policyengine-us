import pytest
from policyengine_us import CountryTaxBenefitSystem, Simulation

DEFAULT_SITUATION = {
    "people": {"person": {}},
    "tax_units": {"tax_unit": {"members": ["person"]}},
    "families": {"family": {"members": ["person"]}},
    "spm_units": {"spm_units": {"members": ["person"]}},
    "households": {"household": {"members": ["person"]}},
}

EXEMPTIONS = (
    "household_income_decile",  # because DEFAULT_SITUATION has no weights
    "spm_unit_income_decile",  # because DEFAULT_SITUATION has no weights
    "income_decile",  # because DEFAULT_SITUATION has no weights
    "tanf_max_amount",
    "tanf",
    "tanf_amount_if_eligible",
    "tanf_countable_income",
    "tanf_initial_employment_deduction",
    "is_tanf_initial_eligible",
    "is_tanf_continuous_eligible",
    "is_tanf_eligible",
    "snap_emergency_allotment_monthly",
)


system = CountryTaxBenefitSystem()

simulation = Simulation(
    tax_benefit_system=system,
    situation=DEFAULT_SITUATION,
)


@pytest.mark.parametrize("variable", system.variables)
def test_variable(variable: str) -> None:
    requires_computation_after = system.variables[
        variable
    ].requires_computation_after
    if requires_computation_after:
        simulation.calculate(requires_computation_after, 2022)
    elif variable not in EXEMPTIONS:
        simulation.calculate(variable, 2022)
