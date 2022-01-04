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
    # TANF provides categorical eligibility for SNAP.
    "meets_snap_categorical_eligibility",
    "snap",
    "is_snap_eligible",
    # SNAP in turn provides categorical eligibility for EBB and Lifeline.
    "is_ebb_eligible",
    "ebb",
    "is_lifeline_eligible",
    "lifeline",
)


@pytest.mark.parametrize("variable", system.variables)
def test_variable(variable: str) -> None:
    if variable not in EXEMPTIONS:
        simulation = builder.build_from_dict(system, DEFAULT_SITUATION)
        simulation.calculate(variable, 2022)
