"""A later year must not depend on which earlier years one simulation calculated.

Inputs here are given for 2024 only, as in a single-year dataset such as the
Enhanced CPS: later years carry inputs over or uprate them. Two defects made a
later year depend on the years calculated before it.

- ``monthly_age`` reads ``age`` one month at a time, and core caches each of
  those month values as a twelfth of the year's age. policyengine-core 3.24.0
  through 3.32.12 carried the latest-starting cached period of any unit into a
  later year, so once a month of 2024 after January had been calculated,
  every person's 2025 age was a twelfth of their 2024 age. Fixed in
  policyengine-core.
- The itemization, SALT and state refundability branches were kept across
  periods. A branch copies its parent's cached arrays when it is created, so
  a branch created in 2024 answered 2025 from a copy without any of the
  parent's 2025 values, unlike the branch a 2025-only simulation creates.
  ``get_branch_for_period`` creates them again for each period.

Each test compares a simulation that calculates the base year first with a
fresh simulation that calculates only the later year. The branch test gives
ages for every year so it runs on any core; the age tests skip until the
installed policyengine-core has the carry-over fix.
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


def _situation(age_every_year=False):
    # Geography has formulas (state_code from state_fips), so it is not
    # carried forward: set it for every year calculated.
    years = (BASE_YEAR, *LATER_YEARS)
    situation = {
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
    if age_every_year:
        # Give age for every year, so no later year carries age over.
        for name, person in situation["people"].items():
            person["age"] = {year: PEOPLE[name]["age"] for year in years}
    return situation


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


@pytest.fixture(scope="module")
def requires_core_carry_over_fix():
    """Skip the age cases on a policyengine-core that still carries a month's
    twelfth into a later year (3.24.0 through 3.32.12). Remove this guard once
    the core minimum includes the fix: until then a core that brought the bug
    back would show here as skips, not failures."""
    simulation = Simulation(situation=_situation())
    simulation.calculate("monthly_age", f"{BASE_YEAR}-12")
    if not np.array_equal(simulation.calculate("age", BASE_YEAR + 1), _input_ages()):
        pytest.skip(
            "needs a policyengine-core release with the auto-carry-over fix "
            "(PolicyEngine/policyengine-core#557 or #562)"
        )


@pytest.mark.parametrize("year", LATER_YEARS)
def test_formula_branches_are_created_again_for_a_later_year(year):
    """The branch defect alone, on any core: ages are given for every year."""
    fresh = _later_year_values(
        Simulation(situation=_situation(age_every_year=True)), year
    )

    simulation = Simulation(situation=_situation(age_every_year=True))
    _later_year_values(simulation, BASE_YEAR)
    branches = ("itemizing", "not_itemizing", "no_salt")
    base_year_branches = {name: simulation.branches[name] for name in branches}

    _assert_same(_later_year_values(simulation, year), fresh, year)
    for name in branches:
        assert simulation.branches[name] is not base_year_branches[name]
        assert simulation.branches[name].branch_period == period(year)


@pytest.mark.usefixtures("requires_core_carry_over_fix")
@pytest.mark.parametrize("month", ["2024-01", "2024-06", "2024-12"])
def test_monthly_age_does_not_change_later_age(month):
    simulation = Simulation(situation=_situation())
    np.testing.assert_array_equal(
        simulation.calculate("monthly_age", month), _input_ages()
    )
    for year in LATER_YEARS:
        np.testing.assert_array_equal(simulation.calculate("age", year), _input_ages())


@pytest.mark.usefixtures("requires_core_carry_over_fix")
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


# State comparison branches: one household per state, with ages given for
# every year so the cases run on any core.

STATE_BRANCH_CASES = [
    (
        "DE",
        ("de_refundable_eitc", "de_non_refundable_eitc"),
        (2024, 2025),
        "de_income_tax",
    ),
    (
        "VA",
        ("va_refundable_eitc", "va_non_refundable_eitc"),
        (2024, 2025),
        "va_income_tax",
    ),
    (
        "ID",
        (
            "id_receives_aged_or_disabled_credit_branch",
            "id_receives_aged_or_disabled_deduction_branch",
        ),
        (2024, 2025),
        "id_income_tax",
    ),
    ("NY", ("pre_tcja_ctc",), (2023, 2024), "ny_income_tax"),
]


def _state_situation(state, years):
    """A low-earning parent aged 67 with one child: EITC-eligible, aged for
    Idaho's credit, and with a child for New York's CTC."""
    members = ["parent", "child"]
    return {
        "people": {
            "parent": {
                "age": {year: 67 for year in years},
                "employment_income": {years[0]: 25_000},
            },
            "child": {"age": {year: 5 for year in years}},
        },
        "tax_units": {"tax_unit": {"members": members}},
        "spm_units": {"spm_unit": {"members": members}},
        "families": {"family": {"members": members}},
        "marital_units": {
            "parent_unit": {"members": ["parent"]},
            "child_unit": {"members": ["child"]},
        },
        "households": {
            "household": {
                "members": members,
                "state_code": {year: state for year in years},
            }
        },
    }


@pytest.mark.parametrize(
    "state,branches,years,variable",
    STATE_BRANCH_CASES,
    ids=[case[0] for case in STATE_BRANCH_CASES],
)
def test_state_comparison_branches_are_created_again_for_a_later_year(
    state, branches, years, variable
):
    first_year, later_year = years
    fresh = Simulation(situation=_state_situation(state, years)).calculate(
        variable, later_year
    )

    simulation = Simulation(situation=_state_situation(state, years))
    simulation.calculate(variable, first_year)
    first_year_branches = {name: simulation.branches[name] for name in branches}

    np.testing.assert_array_equal(simulation.calculate(variable, later_year), fresh)
    for name in branches:
        assert simulation.branches[name] is not first_year_branches[name]
        assert simulation.branches[name].branch_period == period(later_year)


@pytest.mark.parametrize(
    "state,branch,variable",
    [("AL", "al_2020_irc", "al_income_tax"), ("NY", "ny_pre_arpa_eitc", "ny_eitc")],
    ids=["AL", "NY"],
)
def test_2021_only_branches_take_their_period(state, branch, variable):
    """Alabama's 2020-IRC and New York's pre-ARPA EITC branches apply in 2021
    only, so a later year never reuses them; they still record their period."""
    simulation = Simulation(situation=_state_situation(state, (2021,)))
    simulation.calculate(variable, 2021)
    assert simulation.branches[branch].branch_period == period(2021)
