"""Properties of Georgia's claim of right credit and Oklahoma's refund.

Both states give relief for the state tax paid in an earlier year on income
repaid this year only when federal tax is computed under 26 U.S.C.
1341(a)(5), the credit option:

- Georgia: a credit reported with Georgia income tax withheld (2024 and 2025
  IT-511, Form 500 line 25);
- Oklahoma: a refund of the earlier year's tax through an amended return for
  that year (OAC 710:50-3-9), counted in the year of repayment.

Under the deduction option the federal deduction flows to the state's
itemized deductions and there is no state relief.

YAML cases check single households. These tests check properties at every
point of a grid, one vectorized simulation per year and scenario, and compare
the model with independent simulations that have no repayment or that fix the
federal method as an input:

- the relief is the whole prior-year state tax decrease when the federal
  credit applies, and nothing otherwise;
- under the federal credit, state income tax equals the tax of the same filer
  with no repayment, minus the relief (section 1341(b)(3): no deduction is
  taken into account);
- under the federal deduction, the prior-year state tax decrease changes
  nothing;
- relief above the year's tax is refunded;
- state income tax never rises with the prior-year state tax decrease.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

STATES = ["GA", "OK"]
RELIEF = {"GA": "ga_claim_of_right_credit", "OK": "ok_claim_of_right_refund"}
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
YEARS = [2025, 2026]
TOLERANCE = 0.01
METHODS = ["derived", "deduction", "credit"]
VARIABLES = [
    "ga_income_tax",
    "ok_income_tax",
    "ga_claim_of_right_credit",
    "ok_claim_of_right_refund",
    "claim_of_right_credit_applies",
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
            "claim_of_right_prior_year_tax_decrease": {year: FEDERAL_DECREASE[i]},
            state_input: {year: float(state_decrease[i])},
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
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
    out = {v: np.asarray(simulation.calculate(v, year)) for v in VARIABLES}
    # Each tax unit is in one state, so the other state's variables are zero.
    out["state_tax"] = out["ga_income_tax"] + out["ok_income_tax"]
    out["relief"] = out["ga_claim_of_right_credit"] + out["ok_claim_of_right_refund"]
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
            # The federal deduction with no prior-year state tax decrease.
            "deduction_without_decrease": calculate(
                grid_simulation(year, REPAYMENT, zeros, False), year
            ),
            # The same filers with no repayment and no prior-year decrease.
            "none": calculate(grid_simulation(year, zeros, zeros), year),
        }
    return out


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("method", METHODS)
def test_the_relief_follows_the_federal_credit(results, year, method):
    r = results[year][method]
    credit_applies = r["claim_of_right_credit_applies"]
    np.testing.assert_allclose(r["relief"], np.where(credit_applies, STATE_DECREASE, 0))
    for state in STATES:
        assert np.all(r[RELIEF[state]][STATE != state] == 0)
    if method == "derived":
        assert credit_applies.any() and (~credit_applies & (REPAYMENT > 0)).any()


@pytest.mark.parametrize("year", YEARS)
def test_state_tax_under_the_federal_credit(results, year):
    r = results[year]
    expected = r["none"]["state_tax"] - STATE_DECREASE
    np.testing.assert_allclose(r["credit"]["state_tax"], expected, atol=TOLERANCE)
    derived = r["derived"]
    applies = derived["claim_of_right_credit_applies"]
    np.testing.assert_allclose(
        derived["state_tax"][applies], expected[applies], atol=TOLERANCE
    )


@pytest.mark.parametrize("year", YEARS)
def test_the_state_decrease_changes_nothing_under_the_federal_deduction(
    results, year
):
    r = results[year]
    expected = r["deduction_without_decrease"]["state_tax"]
    np.testing.assert_allclose(r["deduction"]["state_tax"], expected, atol=TOLERANCE)
    derived = r["derived"]
    deducts = ~derived["claim_of_right_credit_applies"]
    np.testing.assert_allclose(
        derived["state_tax"][deducts], expected[deducts], atol=TOLERANCE
    )
    assert np.all(r["deduction"]["relief"] == 0)


@pytest.mark.parametrize("year", YEARS)
def test_relief_above_the_tax_is_refunded(results, year):
    r = results[year]["credit"]
    refunded = r["relief"] > results[year]["none"]["state_tax"] + TOLERANCE
    for state in STATES:
        assert (refunded & (STATE == state)).any(), f"no refund case in {state}"
    assert np.all(r["state_tax"][refunded] < 0)


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("method", METHODS)
def test_state_tax_never_rises_with_the_state_decrease(results, year, method):
    table = results[year][method]["state_tax"].reshape(SHAPE)
    assert np.all(np.diff(table, axis=2) <= TOLERANCE)
