"""Properties of the Arizona, Connecticut and Michigan claim of right credits.

Each of these states gives a refundable credit for the state tax paid in an
earlier year on income repaid this year, whichever method 26 U.S.C. 1341
applies to the federal return, and allows no state deduction for the
repayment:

- Arizona: A.R.S. 43-1029 (tax computed without the deduction, minus the
  decrease in the earlier year's Arizona tax, when the repayment exceeds
  $3,000) and A.R.S. 43-1021(9) (the federal deduction is added to Arizona
  gross income);
- Connecticut: Conn. Gen. Stat. 12-711a (federal tax determined under section
  1341(a)(4) or (5));
- Michigan: MCL 206.265 (eligible for a deduction or credit under section
  1341).

YAML cases check single households from each state's own examples. These
tests check properties at every point of a grid, one vectorized simulation
per year and scenario, and compare the model with independent simulations
that have no repayment or that fix the federal method as an input:

- the credit is the whole prior-year state tax decrease or nothing, and it
  is nothing for a repayment of $3,000 or less;
- state income tax equals the tax of the same filer with no repayment, minus
  the credit, under each federal method and under the method the model
  derives;
- a credit above the year's tax is refunded;
- state income tax never rises with the prior-year state tax decrease;
- Arizona's addition is the deduction taken on the federal return, raises
  Arizona adjusted gross income by that amount and leaves Arizona taxable
  income unchanged.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

STATES = ["AZ", "CT", "MI"]
REPAYMENTS = [0, 3_000, 3_001, 10_000, 40_000]
STATE_DECREASES = [0, 150, 2_500]
FEDERAL_DECREASES = [0, 4_000]
WAGES = [0, 30_000, 100_000]
INTEREST = [0, 10_000, 30_000]
AXES = [STATES, REPAYMENTS, STATE_DECREASES, FEDERAL_DECREASES, WAGES, INTEREST]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
STATE = np.array([point[0] for point in GRID])
REPAYMENT, STATE_DECREASE, FEDERAL_DECREASE, WAGE, INTEREST_PAID = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(1, len(AXES))
)
THRESHOLD = 3_000
YEARS = [2025, 2026]
TOLERANCE = 0.01
METHODS = ["derived", "deduction", "credit"]
STATE_VARIABLES = [
    "az_income_tax",
    "ct_income_tax",
    "mi_income_tax",
    "az_claim_of_right_credit",
    "ct_claim_of_right_credit",
    "mi_claim_of_right_credit",
    "az_claim_of_right_addition",
    "az_agi",
    "az_taxable_income",
    "claim_of_right_deduction",
    "claim_of_right_credit_applies",
    "tax_unit_itemizes",
]


def grid_simulation(year, repayment, state_decrease, credit_applies=None):
    """One single-person tax unit per grid point, in the point's state."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        state_input = f"{STATE[i].lower()}_claim_of_right_prior_year_tax_decrease"
        situation["people"][person] = {
            "age": {year: 40},
            "employment_income": {year: WAGE[i]},
            "claim_of_right_repayment": {year: float(repayment[i])},
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            "claim_of_right_prior_year_tax_decrease": {year: FEDERAL_DECREASE[i]},
            state_input: {year: float(state_decrease[i])},
            "interest_deduction": {year: INTEREST_PAID[i]},
        }
        if credit_applies is not None:
            situation["tax_units"][f"t{i}"]["claim_of_right_credit_applies"] = {
                year: credit_applies
            }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: str(STATE[i])},
        }
    return Simulation(situation=situation)


def calculate(simulation, year):
    out = {v: np.asarray(simulation.calculate(v, year)) for v in STATE_VARIABLES}
    # Each tax unit is in one state, so the other states' variables are zero.
    out["state_tax"] = sum(out[f"{state.lower()}_income_tax"] for state in STATES)
    out["credit"] = sum(
        out[f"{state.lower()}_claim_of_right_credit"] for state in STATES
    )
    return out


@pytest.fixture(scope="module")
def results():
    zeros = np.zeros_like(REPAYMENT)
    out = {}
    for year in YEARS:
        out[year] = {
            "derived": calculate(
                grid_simulation(year, REPAYMENT, STATE_DECREASE), year
            ),
            "deduction": calculate(
                grid_simulation(year, REPAYMENT, STATE_DECREASE, False), year
            ),
            "credit": calculate(
                grid_simulation(year, REPAYMENT, STATE_DECREASE, True), year
            ),
            # The same filers with no repayment and no prior-year decrease.
            "none": calculate(grid_simulation(year, zeros, zeros), year),
        }
    return out


def eligible():
    return REPAYMENT > THRESHOLD


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("method", METHODS)
def test_the_credit_is_the_whole_decrease_or_nothing(results, year, method):
    r = results[year][method]
    np.testing.assert_allclose(r["credit"], np.where(eligible(), STATE_DECREASE, 0))
    for state in STATES:
        elsewhere = STATE != state
        assert np.all(r[f"{state.lower()}_claim_of_right_credit"][elsewhere] == 0)


@pytest.mark.parametrize("year", YEARS)
def test_both_federal_methods_occur(results, year):
    r = results[year]["derived"]
    assert (eligible() & r["claim_of_right_credit_applies"]).any()
    assert (eligible() & ~r["claim_of_right_credit_applies"]).any()
    assert (r["claim_of_right_deduction"] > 0)[r["tax_unit_itemizes"]].any()


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("method", METHODS)
def test_state_tax_is_the_tax_without_the_repayment_less_the_credit(
    results, year, method
):
    r = results[year][method]
    expected = results[year]["none"]["state_tax"] - np.where(
        eligible(), STATE_DECREASE, 0
    )
    np.testing.assert_allclose(r["state_tax"], expected, atol=TOLERANCE)


@pytest.mark.parametrize("year", YEARS)
def test_a_credit_above_the_tax_is_refunded(results, year):
    r = results[year]["derived"]
    refunded = r["credit"] > results[year]["none"]["state_tax"] + TOLERANCE
    for state in STATES:
        assert (refunded & (STATE == state)).any(), f"no refund case in {state}"
    assert np.all(r["state_tax"][refunded] < 0)


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("method", METHODS)
def test_state_tax_never_rises_with_the_state_decrease(results, year, method):
    table = results[year][method]["state_tax"].reshape(SHAPE)
    assert np.all(np.diff(table, axis=2) <= TOLERANCE)


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("method", METHODS)
def test_arizona_adds_back_the_federal_deduction_without_taxing_it(
    results, year, method
):
    r = results[year][method]
    none = results[year]["none"]
    arizona = STATE == "AZ"
    addition = r["az_claim_of_right_addition"]
    np.testing.assert_allclose(
        addition,
        np.where(arizona, r["claim_of_right_deduction"] * r["tax_unit_itemizes"], 0),
    )
    np.testing.assert_allclose(r["az_agi"], none["az_agi"] + addition)
    np.testing.assert_allclose(
        r["az_taxable_income"], none["az_taxable_income"], atol=TOLERANCE
    )
    if method == "credit":
        # Section 1341(b)(3): under (a)(5) there is no deduction to add back.
        assert np.all(addition == 0)
    else:
        assert (addition[arizona] > 0).any(), "the grid should include an addition"
