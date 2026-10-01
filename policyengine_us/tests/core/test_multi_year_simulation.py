"""A later year must not depend on which earlier years one simulation calculated.

Inputs here are given for 2024 only, as in a single-year dataset such as the
Enhanced CPS: later years carry inputs over or uprate them. Two defects made a
later year depend on the years calculated before it.

- ``monthly_age`` reads ``age`` one month at a time, and core caches each of
  those month values as a twelfth of the year's age. policyengine-core 3.24.0
  through 3.32.11 carried the latest-starting cached period of any unit into a
  later year, so once a month of 2024 after January had been calculated,
  every person's 2025 age was a twelfth of their 2024 age. Fixed in
  policyengine-core.
- The itemization, SALT and state refundability branches were kept across
  periods. A branch copies its parent's cached arrays when it is created, so
  a branch created in 2024 answered 2025 from a copy without any of the
  parent's 2025 values, unlike the branch a 2025-only simulation creates.
  ``get_branch_for_period`` creates them again for each period.

Each test compares a simulation that calculates the base year first with a
fresh simulation that calculates only the later year.
"""

import numpy as np
import pytest
from policyengine_core.periods import period

from policyengine_us import Simulation

BASE_YEAR = 2024
LATER_YEARS = (2025, 2027)
STATES = {"il": "IL", "ca": "CA", "tx": "TX"}

PEOPLE = {
    # An Illinois single parent with two young children in paid childcare:
    # Illinois CCAP reads monthly_age.
    "il_parent": {"age": 34, "employment_income": 30_000},
    "il_child_1": {"age": 3, "pre_subsidy_childcare_expenses": 9_000},
    "il_child_2": {"age": 7, "pre_subsidy_childcare_expenses": 4_000},
    # A California couple who itemize, so the itemizing and not_itemizing
    # branches decide their income tax.
    "ca_head": {
        "age": 52,
        "employment_income": 180_000,
        "deductible_mortgage_interest": 25_000,
        "real_estate_taxes": 15_000,
        "charitable_cash_donations": 10_000,
    },
    "ca_spouse": {"age": 50, "employment_income": 60_000},
    "ca_child": {"age": 15},
    # A Texas retiree, whose age decides the senior deductions.
    "tx_retiree": {
        "age": 70,
        "social_security_retirement": 24_000,
        "taxable_interest_income": 8_000,
    },
}
UNITS = {
    "il": ["il_parent", "il_child_1", "il_child_2"],
    "ca": ["ca_head", "ca_spouse", "ca_child"],
    "tx": ["tx_retiree"],
}
MARITAL_UNITS = [
    ["il_parent"],
    ["il_child_1"],
    ["il_child_2"],
    ["ca_head", "ca_spouse"],
    ["ca_child"],
    ["tx_retiree"],
]

VARIABLES = [
    "age",
    "is_tax_unit_dependent",
    "filing_status",
    "adjusted_gross_income",
    "taxable_income",
    "tax_unit_itemizes",
    "tax_liability_if_itemizing",
    "tax_liability_if_not_itemizing",
    "ctc_limiting_tax_liability",
    "income_tax",
    "eitc",
    "refundable_ctc",
    "state_income_tax",
    "household_net_income",
]


def _situation():
    # Geography has formulas (state_code from state_fips), so it is not
    # carried forward: set it for every year calculated.
    years = (BASE_YEAR, *LATER_YEARS)
    return {
        "people": {
            name: {variable: {BASE_YEAR: value} for variable, value in inputs.items()}
            for name, inputs in PEOPLE.items()
        },
        "tax_units": {key: {"members": members} for key, members in UNITS.items()},
        "spm_units": {key: {"members": members} for key, members in UNITS.items()},
        "families": {key: {"members": members} for key, members in UNITS.items()},
        "marital_units": {
            f"marital_unit_{i}": {"members": members}
            for i, members in enumerate(MARITAL_UNITS)
        },
        "households": {
            key: {
                "members": members,
                "state_code": {year: STATES[key] for year in years},
            }
            for key, members in UNITS.items()
        },
    }


def _input_ages():
    return np.array([inputs["age"] for inputs in PEOPLE.values()], dtype=float)


def _later_year_values(simulation, year):
    return {
        variable: np.asarray(simulation.calculate(variable, year))
        for variable in VARIABLES
    }


def _assert_same(result, fresh, year):
    for variable in VARIABLES:
        np.testing.assert_array_equal(
            result[variable],
            fresh[variable],
            err_msg=f"{variable} for {year} depends on earlier years calculated",
        )


@pytest.mark.parametrize("month", ["2024-01", "2024-06", "2024-12"])
def test_monthly_age_does_not_change_later_age(month):
    simulation = Simulation(situation=_situation())
    np.testing.assert_array_equal(
        simulation.calculate("monthly_age", month), _input_ages()
    )
    for year in LATER_YEARS:
        np.testing.assert_array_equal(simulation.calculate("age", year), _input_ages())


@pytest.mark.parametrize("year", LATER_YEARS)
def test_later_year_matches_single_year_simulation(year):
    fresh = _later_year_values(Simulation(situation=_situation()), year)
    np.testing.assert_array_equal(fresh["age"], _input_ages())

    simulation = Simulation(situation=_situation())
    _later_year_values(simulation, BASE_YEAR)
    BRANCHES = ("itemizing", "not_itemizing", "no_salt")
    base_year_branches = {name: simulation.branches[name] for name in BRANCHES}
    # Request every month of the base year too, as monthly programs do for
    # people they cover.
    for month in range(1, 13):
        simulation.calculate("monthly_age", f"{BASE_YEAR}-{month:02d}")

    _assert_same(_later_year_values(simulation, year), fresh, year)
    # The itemization branches were created again for the later year rather
    # than kept from the base year.
    for name in BRANCHES:
        assert simulation.branches[name] is not base_year_branches[name]
        assert simulation.branches[name].branch_period == period(year)
