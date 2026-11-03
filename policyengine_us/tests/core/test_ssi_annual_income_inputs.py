"""SSI monthly budgets must preserve existing annual input overrides.

Policy examples and monthly allocation caps are covered in YAML. These tests
exercise Core's period conversion, supplied-input detection and branch caches,
which require the Python API. One small Core system uses the production
variable classes and the imported country's read-only parameters; it never
constructs or copies another country model. This belongs to Rest/core.
"""

import numpy as np
import pytest
from policyengine_core.simulations import Simulation
from policyengine_core.taxbenefitsystems import TaxBenefitSystem

from policyengine_us.entities import MaritalUnit, Person
from policyengine_us.system import system as country_system
from policyengine_us.tools.period_branch import get_override_branch

YEAR = 2026
MONTH = "2026-01"
ANNUAL_CURRENCY_VARIABLES = (
    "ssi_countable_income",
    "ssi_unearned_income_deemed_from_ineligible_parent",
    "ssi_earned_income_deemed_from_ineligible_spouse",
    "ssi_unearned_income_deemed_from_ineligible_spouse",
    "ssi_income_deemed_from_ineligible_spouse",
    "ssi_ineligible_child_allocation",
    "ssi_in_kind_support_and_maintenance",
    "ssi_pmv_amount",
    "medicaid_optional_senior_or_disabled_countable_income",
    "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
    "medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse",
)

ANNUAL_INPUT_VARIABLES = (*ANNUAL_CURRENCY_VARIABLES, "is_ssi_spousal_deeming_applies")


@pytest.fixture(scope="module")
def small_system():
    result = TaxBenefitSystem(entities=[Person, MaritalUnit])
    names = (
        "is_ssi_eligible_individual",
        "is_ssi_ineligible_spouse",
        "ssi_earned_income",
        "ssi_unearned_income",
        "ssi_spousal_deeming_child_allocations",
        *ANNUAL_INPUT_VARIABLES,
        *(f"{name}_monthly" for name in ANNUAL_INPUT_VARIABLES),
    )
    result.add_variables(*(type(country_system.variables[name]) for name in names))
    result.parameters = country_system.parameters
    return result


@pytest.mark.parametrize("input_period", [YEAR, MONTH])
@pytest.mark.parametrize("name", ANNUAL_INPUT_VARIABLES)
def test_annual_input_overrides_reach_monthly_budgets(small_system, name, input_period):
    amount = 1_200 if name in ANNUAL_CURRENCY_VARIABLES else True
    monthly = 100 if name in ANNUAL_CURRENCY_VARIABLES else True
    changed = 2_400 if name in ANNUAL_CURRENCY_VARIABLES else False
    changed_monthly = 200 if name in ANNUAL_CURRENCY_VARIABLES else False
    simulation = Simulation(
        tax_benefit_system=small_system,
        situation={
            "people": {
                "claimant": {
                    name: {input_period: amount},
                    # Supplied inputs bypass the formula's eligibility gate.
                    "is_ssi_eligible_individual": {YEAR: False},
                }
            },
            "marital_units": {"unit": {"members": ["claimant"]}},
        },
    )
    assert small_system.variables[name].definition_period == "year"
    np.testing.assert_array_equal(simulation.calculate(name, YEAR), [amount])
    np.testing.assert_array_equal(simulation.calculate(name, MONTH), [monthly])
    np.testing.assert_array_equal(
        simulation.calculate(f"{name}_monthly", MONTH), [monthly]
    )

    branch = get_override_branch(
        simulation, "annual_override", YEAR, {name: np.array([changed])}
    )
    np.testing.assert_array_equal(
        branch.calculate(f"{name}_monthly", MONTH), [changed_monthly]
    )
    np.testing.assert_array_equal(
        simulation.calculate(f"{name}_monthly", MONTH), [monthly]
    )


def test_computed_annual_cache_does_not_replace_monthly_budgets(small_system):
    name = "ssi_earned_income_deemed_from_ineligible_spouse"
    allocations = {
        f"2026-{month:02d}": 0 if month <= 6 else 200 for month in range(1, 13)
    }
    simulation = Simulation(
        tax_benefit_system=small_system,
        situation={
            "people": {
                "claimant": {
                    "is_ssi_ineligible_spouse": {YEAR: False},
                    "ssi_earned_income": {YEAR: 0},
                    "ssi_unearned_income": {YEAR: 0},
                    "ssi_spousal_deeming_child_allocations": allocations,
                },
                "spouse": {
                    "is_ssi_ineligible_spouse": {YEAR: True},
                    "ssi_earned_income": {YEAR: 12_000},
                    "ssi_unearned_income": {YEAR: 0},
                    "ssi_spousal_deeming_child_allocations": {
                        month: 0 for month in allocations
                    },
                },
            },
            "marital_units": {"couple": {"members": ["claimant", "spouse"]}},
        },
    )
    # Six months of $1,000 and six of $800 are not $900 in every month.
    np.testing.assert_array_equal(simulation.calculate(name, YEAR), [10_800, 0])
    np.testing.assert_array_equal(
        simulation.calculate(f"{name}_monthly", MONTH), [1_000, 0]
    )
    np.testing.assert_array_equal(
        simulation.calculate(f"{name}_monthly", "2026-07"), [800, 0]
    )

    if hasattr(simulation, "_get_store_history"):
        # Core 3.33+ invalidates inherited calculations on direct set_input.
        branch = simulation.get_branch("first_annual_override")
        branch.set_input(name, YEAR, [24_000, 0])
    else:
        branch = get_override_branch(
            simulation, "first_annual_override", YEAR, {name: np.array([24_000, 0])}
        )
    np.testing.assert_array_equal(
        branch.calculate(f"{name}_monthly", MONTH), [2_000, 0]
    )
    np.testing.assert_array_equal(
        simulation.calculate(f"{name}_monthly", MONTH), [1_000, 0]
    )
