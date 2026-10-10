"""Branch isolation and cross-case properties of the section 1341 computation.

26 U.S.C. 1341(a): when a filer repays more than $3,000 of income included in
an earlier year under a claim of right, federal tax is the lesser of (4) the
tax with a deduction for the repayment and (5) the tax without it minus the
decrease in the earlier year's tax from excluding the income. Ties use (4)
(26 CFR 1.1341-1(b)(3)); any excess of the decrease over the tax is refunded
(1341(b)(1)). North Carolina allows no claim of right deduction under
1341(a)(5) (G.S. 105-153.5(a)(2)d) and instead treats the increase in the
earlier year's North Carolina tax as a payment (G.S. 105-266.2).

The policy cases are in YAML (``gov/irs/credits/claim_of_right``). These tests
cover what a YAML case cannot. The model picks the method by calculating
federal tax in two override branches, so the tests build separate simulations
and compare them:

- each branch equals a simulation that fixes the method as an input before
  anything is calculated, and income tax equals the smaller of the two
  (ties to the deduction), where the credit side comes from a simulation with
  no repayment at all less the prior-year decrease;
- results do not depend on which variable is calculated first, including
  when a tax liability under one itemizing choice is calculated before the
  method is known;
- a later year calculated on the same simulation equals a simulation of that
  year alone;
- relations between cases over a grid: tax never rises with the repayment
  (also across the $3,000 threshold) or with the prior-year decrease, and a
  repayment of $3,000 or less changes nothing (section 67(h), formerly 67(g)).

They also check, at every grid point, that the deduction is the whole
repayment or nothing, the credit is the whole decrease or nothing, and never
both; that North Carolina's deduction is zero whenever the credit method
applies and otherwise is what it is with the deduction method fixed; and that
its payment is the prior-year increase when the credit method applies and zero
otherwise.

Last, one itemizing household per state: with the credit method fixed, the
repayment leaves every state's income tax unchanged in the model (no state
input is supplied), and with the deduction method fixed it leaves Arizona's,
California's, Kansas's and Wisconsin's unchanged.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)

REPAYMENTS = [0, 2_999, 3_000, 3_001, 5_000, 20_000, 150_000]
DECREASES = [0, 400, 2_500, 12_000, 60_000]
WAGES = [0, 30_000, 80_000, 400_000, 1_500_000]
CHARITY = [0, 20_000]
AXES = [REPAYMENTS, DECREASES, WAGES, CHARITY]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
REPAYMENT, DECREASE, WAGE, CHARITABLE = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(len(AXES))
)
# An illustrative North Carolina prior-year tax increase on the repaid income.
NC_INCREASE = 0.05 * REPAYMENT
ZEROS = np.zeros_like(REPAYMENT)
THRESHOLD = 3_000
YEARS = [2025, 2026]
TOLERANCE = 0.01
# The 50 states and the District of Columbia.
STATES = [
    state.name
    for state in StateCode
    if state.name not in {"AA", "AE", "AP", "AS", "GU", "MP", "PR", "PW", "VI"}
]
# States whose own rules leave out the federal claim of right repayment
# deduction: A.R.S. 43-1021(9), the California Schedule CA (540) instructions
# for Part II line 16, K.S.A. 79-32,120(a) and Wisconsin Form 1 Schedule 1.
STATES_WITHOUT_THE_DEDUCTION = ["AZ", "CA", "KS", "WI"]
BRANCHES = [
    "income_tax_if_claiming_claim_of_right_deduction",
    "income_tax_if_claiming_claim_of_right_credit",
]
VARIABLES = [
    "income_tax",
    "tax_unit_itemizes",
    "tax_liability_if_itemizing",
    "tax_liability_if_not_itemizing",
    "claim_of_right_section_1341_eligible",
    "claim_of_right_credit_applies",
    "claim_of_right_deduction",
    "claim_of_right_credit",
    "nc_claim_of_right_deduction",
    "nc_claim_of_right_payment",
    "nc_income_tax_before_refundable_credits",
    "nc_income_tax",
] + BRANCHES


def grid_simulation(
    years, repayment=REPAYMENT, decrease=DECREASE, nc_increase=NC_INCREASE, method=None
):
    """One single-person North Carolina tax unit per grid point."""

    def yearly(value):
        return {year: value for year in years}

    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": yearly(40),
            "employment_income": yearly(WAGE[i]),
            "charitable_cash_donations": yearly(CHARITABLE[i]),
            "claim_of_right_repayment": yearly(float(repayment[i])),
        }
        tax_unit = {
            "members": [person],
            "claim_of_right_prior_year_tax_decrease": yearly(float(decrease[i])),
            "nc_claim_of_right_prior_year_tax_increase": yearly(float(nc_increase[i])),
        }
        if method is not None:
            tax_unit["claim_of_right_credit_applies"] = yearly(method)
        situation["tax_units"][f"t{i}"] = tax_unit
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": yearly("NC"),
        }
    return Simulation(situation=situation)


def calculate(simulation, year, variables):
    return {v: np.asarray(simulation.calculate(v, year)) for v in variables}


@pytest.fixture(scope="module")
def results():
    out = {}
    for year in YEARS:
        out[year] = calculate(grid_simulation([year]), year, VARIABLES)
        # Independent references: no repayment at all, and each method fixed
        # as an input rather than chosen in a branch.
        none = grid_simulation([year], ZEROS, ZEROS, ZEROS)
        out[year]["tax_without_repayment"] = np.asarray(
            none.calculate("income_tax", year)
        )
        deduction = grid_simulation([year], method=False)
        out[year]["tax_with_deduction"] = np.asarray(
            deduction.calculate("income_tax", year)
        )
        out[year]["nc_deduction_if_deduction"] = np.asarray(
            deduction.calculate("nc_claim_of_right_deduction", year)
        )
        credit = grid_simulation([year], method=True)
        out[year]["nc_deduction_if_credit"] = np.asarray(
            credit.calculate("nc_claim_of_right_deduction", year)
        )
    return out


def eligible():
    return REPAYMENT > THRESHOLD


@pytest.mark.parametrize("year", YEARS)
def test_tax_is_the_lesser_of_the_two_methods(results, year):
    r = results[year]
    tax_with_deduction = r["tax_with_deduction"]
    tax_with_credit = r["tax_without_repayment"] - DECREASE
    # Compared to the cent; equal amounts keep the deduction.
    credit = eligible() & (
        np.round(tax_with_credit, 2) < np.round(tax_with_deduction, 2)
    )
    assert credit.any() and (eligible() & ~credit).any(), "both methods occur"
    np.testing.assert_array_equal(r["claim_of_right_credit_applies"], credit)
    expected = np.where(
        eligible(),
        np.where(credit, tax_with_credit, tax_with_deduction),
        r["tax_without_repayment"],
    )
    np.testing.assert_allclose(r["income_tax"], expected, atol=TOLERANCE)


@pytest.mark.parametrize("year", YEARS)
def test_branches_match_independent_simulations(results, year):
    r = results[year]
    np.testing.assert_allclose(
        r["income_tax_if_claiming_claim_of_right_deduction"],
        r["tax_with_deduction"],
        atol=TOLERANCE,
    )
    tax_with_credit = r["tax_without_repayment"] - DECREASE
    np.testing.assert_allclose(
        r["income_tax_if_claiming_claim_of_right_credit"][eligible()],
        tax_with_credit[eligible()],
        atol=TOLERANCE,
    )


@pytest.mark.parametrize(
    "first", ["tax_liability_if_itemizing", "tax_liability_if_not_itemizing"] + BRANCHES
)
def test_results_do_not_depend_on_calculation_order(results, first):
    # A tax liability under one itemizing choice is calculated in a branch.
    # Asked for before the method is known, it must not leave a value behind
    # that a later method branch reuses.
    year = YEARS[0]
    simulation = grid_simulation([year])
    simulation.calculate(first, year)
    for variable in VARIABLES:
        np.testing.assert_allclose(
            np.asarray(simulation.calculate(variable, year)),
            results[year][variable],
            atol=TOLERANCE,
            err_msg=f"{variable} changes when {first} is calculated first",
        )


def test_a_later_year_matches_a_simulation_of_that_year_alone(results):
    simulation = grid_simulation(YEARS)
    simulation.calculate("income_tax", YEARS[0])
    for variable in VARIABLES:
        np.testing.assert_allclose(
            np.asarray(simulation.calculate(variable, YEARS[1])),
            results[YEARS[1]][variable],
            atol=TOLERANCE,
            err_msg=f"{variable} differs after an earlier year was calculated",
        )


@pytest.mark.parametrize("year", YEARS)
def test_deduction_and_credit_are_all_or_nothing_and_exclusive(results, year):
    r = results[year]
    credit_applies = r["claim_of_right_credit_applies"]
    deduction = r["claim_of_right_deduction"]
    credit = r["claim_of_right_credit"]
    np.testing.assert_array_equal(r["claim_of_right_section_1341_eligible"], eligible())
    np.testing.assert_allclose(
        deduction, np.where(eligible() & ~credit_applies, REPAYMENT, 0)
    )
    np.testing.assert_allclose(credit, np.where(credit_applies, DECREASE, 0))
    assert not np.any((deduction > 0) & (credit > 0))


@pytest.mark.parametrize("year", YEARS)
def test_a_repayment_of_3000_or_less_changes_nothing(results, year):
    r = results[year]
    small = ~eligible()
    assert not r["claim_of_right_credit_applies"][small].any()
    np.testing.assert_allclose(
        r["income_tax"][small], r["tax_without_repayment"][small], atol=TOLERANCE
    )


@pytest.mark.parametrize("year", YEARS)
def test_tax_never_rises(results, year):
    r = results[year]
    assert np.all(r["income_tax"] <= r["tax_without_repayment"] + TOLERANCE)
    table = r["income_tax"].reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) <= TOLERANCE), "rises with the repayment"
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises with the decrease"


@pytest.mark.parametrize("year", YEARS)
def test_a_decrease_above_the_tax_is_refunded(results, year):
    r = results[year]
    credit_applies = r["claim_of_right_credit_applies"]
    refunded = credit_applies & (DECREASE > r["tax_without_repayment"])
    assert refunded.any(), "the grid should include refunds"
    assert np.all(r["income_tax"][refunded] < 0)


@pytest.mark.parametrize("year", YEARS)
def test_north_carolina_follows_the_federal_method(results, year):
    r = results[year]
    credit_applies = r["claim_of_right_credit_applies"]
    np.testing.assert_allclose(
        r["nc_claim_of_right_deduction"],
        np.where(credit_applies, 0, r["nc_deduction_if_deduction"]),
    )
    assert np.all(r["nc_deduction_if_credit"] == 0)
    np.testing.assert_allclose(
        r["nc_claim_of_right_payment"], np.where(credit_applies, NC_INCREASE, 0)
    )
    np.testing.assert_allclose(
        r["nc_income_tax"],
        r["nc_income_tax_before_refundable_credits"] - r["nc_claim_of_right_payment"],
        atol=TOLERANCE,
    )


def state_income_tax(year, repayment, method=None):
    """State income tax of an itemizing single filer in each state."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, state in enumerate(STATES):
        situation["people"][f"p{i}"] = {
            "age": {year: 40},
            "employment_income": {year: 60_000},
            "charitable_cash_donations": {year: 25_000},
            "claim_of_right_repayment": {year: repayment},
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [f"p{i}"],
            "claim_of_right_prior_year_tax_decrease": {year: 2_500},
        }
        if method is not None:
            situation["tax_units"][f"t{i}"]["claim_of_right_credit_applies"] = {
                year: method
            }
        situation["households"][f"h{i}"] = {
            "members": [f"p{i}"],
            "state_code": {year: state},
        }
    simulation = Simulation(situation=situation)
    return np.asarray(simulation.calculate("state_income_tax", year))


def test_states_under_each_federal_method():
    # One year: each of these three simulations computes every state's tax.
    year = YEARS[0]
    without_repayment = state_income_tax(year, 0)
    with_credit = state_income_tax(year, 10_000, method=True)
    np.testing.assert_allclose(with_credit, without_repayment, atol=TOLERANCE)
    with_deduction = state_income_tax(year, 10_000, method=False)
    assert np.any(np.abs(with_deduction - without_repayment) > 1), (
        "the deduction should reach the states that follow federal itemized deductions"
    )
    excluded = np.isin(STATES, STATES_WITHOUT_THE_DEDUCTION)
    np.testing.assert_allclose(
        with_deduction[excluded], without_repayment[excluded], atol=TOLERANCE
    )
