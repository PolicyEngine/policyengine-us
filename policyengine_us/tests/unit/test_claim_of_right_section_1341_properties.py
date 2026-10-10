"""Properties of the section 1341 claim of right computation.

26 U.S.C. 1341(a): when a filer repays more than $3,000 of income included in
an earlier year under a claim of right, federal tax is the lesser of (4) the
tax with a deduction for the repayment and (5) the tax without it minus the
decrease in the earlier year's tax from excluding the income. Ties use (4)
(26 CFR 1.1341-1(b)(3)); any excess of the decrease over the tax is refunded
(1341(b)(1)). North Carolina allows no claim of right deduction under
1341(a)(5) (G.S. 105-153.5(a)(2)d) and instead treats the increase in the
earlier year's North Carolina tax as a payment (G.S. 105-266.2).

Four more states tie their own rule to the federal method. Under 1341(a)(5)
Maryland (Administrative Release 40) and Virginia (P.D. 16-183, P.D. 20-35)
credit the state's own prior-year tax on the repaid income, and Nebraska
(Neb. Rev. Stat. 77-2716(7)) and Louisiana (Revenue Ruling 04-002) subtract
the amount repaid from income. Under 1341(a)(4) none of the four adjusts.

YAML cases check single households from Publication 525. These tests check
properties at every point of a grid, one vectorized simulation per year and
scenario, and compare the model's branch computations with independent
simulations that fix the method as an input:

- the lesser-of rule: income tax equals the smaller of the tax with the
  deduction method fixed and the tax with no repayment at all less the
  prior-year decrease, ties going to the deduction;
- the branches agree with those independent simulations;
- the deduction is the whole repayment or nothing, the credit is the whole
  decrease or nothing, and never both;
- a repayment of $3,000 or less changes nothing (section 67(g));
- the computation never raises tax, and tax never rises with the repayment
  (also across the $3,000 threshold) or with the prior-year decrease;
- North Carolina's deduction is zero exactly when the credit method applies,
  and its payment is then the prior-year North Carolina tax increase;
- Maryland's and Virginia's credits are the state's prior-year tax exactly
  when the credit method applies, lower state tax by exactly that much, and
  are refunded past zero; Nebraska's and Louisiana's subtractions are the
  amount repaid exactly when the credit method applies and lower state
  adjusted gross income by that much;
- under the credit method the repayment changes no other state's income tax
  (section 1341(b)(3): the deduction is not taken into account for any other
  purpose), and under the deduction method it changes none in Arizona, Kansas
  or Wisconsin, whose laws leave the federal deduction out.
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
THRESHOLD = 3_000
YEARS = [2025, 2026]
TOLERANCE = 0.01
# The 50 states and the District of Columbia.
STATES = [
    state.name
    for state in StateCode
    if state.name not in {"AA", "AE", "AP", "AS", "GU", "MP", "PR", "PW", "VI"}
]
# States whose itemized deductions leave out the federal claim of right
# repayment deduction: A.R.S. 43-1021(9), K.S.A. 79-32,120(a) and Wis. Stat.
# 71.07(5)(a)7.
STATES_WITHOUT_THE_DEDUCTION = ["AZ", "KS", "WI"]
# States that, under the federal credit method, credit their own prior-year
# tax on the repaid income, with the input each uses: Maryland Administrative
# Release 40, G.S. 105-266.2 and Virginia P.D. 16-183.
STATE_PRIOR_YEAR_TAX_INPUTS = {
    "MD": "md_claim_of_right_prior_year_tax_decrease",
    "NC": "nc_claim_of_right_prior_year_tax_increase",
    "VA": "va_claim_of_right_prior_year_tax_decrease",
}
STATE_CREDITS = {
    "MD": "md_claim_of_right_credit",
    "VA": "va_claim_of_right_credit",
}
# States that, under the federal credit method, subtract the amount repaid
# from income, with the state's adjusted gross income: Louisiana Revenue
# Ruling 04-002 and Neb. Rev. Stat. 77-2716(7).
STATE_SUBTRACTIONS = {
    "LA": ("la_claim_of_right_deduction", "la_agi"),
    "NE": ("ne_claim_of_right_subtraction", "ne_agi"),
}
STATE_GRID_STATES = sorted([*STATE_CREDITS, *STATE_SUBTRACTIONS])
# An illustrative state prior-year tax on the repaid income.
STATE_PRIOR_YEAR_TAX = 0.04 * REPAYMENT
VARIABLES = [
    "income_tax",
    "claim_of_right_section_1341_eligible",
    "claim_of_right_credit_applies",
    "claim_of_right_deduction",
    "claim_of_right_credit",
    "nc_claim_of_right_deduction",
    "nc_claim_of_right_payment",
    "nc_income_tax_before_refundable_credits",
    "nc_income_tax",
]


def grid_simulation(year, repayment, decrease, nc_increase, tax_units=None):
    """One single-person North Carolina tax unit per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            "employment_income": {year: WAGE[i]},
            "charitable_cash_donations": {year: CHARITABLE[i]},
            "claim_of_right_repayment": {year: float(repayment[i])},
            "claim_of_right_prior_year_tax_decrease": {year: float(decrease[i])},
            "nc_claim_of_right_prior_year_tax_increase": {year: float(nc_increase[i])},
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            **{
                name: {year: bool(values[i])}
                for name, values in (tax_units or {}).items()
            },
        }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "NC"},
        }
    return Simulation(situation=situation)


def calculate(simulation, year, variables):
    return {v: np.asarray(simulation.calculate(v, year)) for v in variables}


@pytest.fixture(scope="module")
def results():
    zeros = np.zeros_like(REPAYMENT)
    ones = np.ones_like(REPAYMENT)
    out = {}
    for year in YEARS:
        model = grid_simulation(year, REPAYMENT, DECREASE, NC_INCREASE)
        out[year] = calculate(
            model,
            year,
            VARIABLES
            + [
                "income_tax_if_claiming_claim_of_right_deduction",
                "income_tax_if_claiming_claim_of_right_credit",
            ],
        )
        # Independent references: no repayment at all, and the deduction
        # method fixed as an input rather than chosen in a branch.
        none = grid_simulation(year, zeros, zeros, zeros)
        out[year]["tax_without_repayment"] = np.asarray(
            none.calculate("income_tax", year)
        )
        deduction = grid_simulation(
            year,
            REPAYMENT,
            DECREASE,
            NC_INCREASE,
            {"claim_of_right_credit_applies": zeros},
        )
        out[year]["tax_with_deduction"] = np.asarray(
            deduction.calculate("income_tax", year)
        )
        credit = grid_simulation(
            year,
            REPAYMENT,
            DECREASE,
            NC_INCREASE,
            {"claim_of_right_credit_applies": ones},
        )
        out[year]["nc_deduction_if_credit"] = np.asarray(
            credit.calculate("nc_claim_of_right_deduction", year)
        )
        out[year]["nc_deduction_if_deduction"] = np.asarray(
            deduction.calculate("nc_claim_of_right_deduction", year)
        )
    return out


def eligible():
    return REPAYMENT > THRESHOLD


@pytest.mark.parametrize("year", YEARS)
def test_tax_is_the_lesser_of_the_two_methods(results, year):
    r = results[year]
    tax_with_deduction = r["tax_with_deduction"]
    tax_with_credit = r["tax_without_repayment"] - DECREASE
    credit = eligible() & (tax_with_credit < tax_with_deduction - TOLERANCE)
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


def state_grid_simulation(year, repayment, decrease, state_prior_year_tax):
    """One single-person tax unit per grid point in each state with a rule."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for s, state in enumerate(STATE_GRID_STATES):
        for i in range(len(GRID)):
            person = f"p{s}_{i}"
            situation["people"][person] = {
                "age": {year: 40},
                "employment_income": {year: WAGE[i]},
                "charitable_cash_donations": {year: CHARITABLE[i]},
                "claim_of_right_repayment": {year: float(repayment[i])},
                "claim_of_right_prior_year_tax_decrease": {year: float(decrease[i])},
                **{
                    name: {year: float(state_prior_year_tax[i])}
                    for name in STATE_PRIOR_YEAR_TAX_INPUTS.values()
                },
            }
            situation["tax_units"][f"t{s}_{i}"] = {"members": [person]}
            situation["households"][f"h{s}_{i}"] = {
                "members": [person],
                "state_code": {year: state},
            }
    return Simulation(situation=situation)


@pytest.fixture(scope="module")
def state_results():
    # One year: these two simulations compute four states' taxes at every
    # grid point.
    year = 2025
    zeros = np.zeros_like(REPAYMENT)
    variables = [
        "claim_of_right_credit_applies",
        "state_income_tax",
        *STATE_CREDITS.values(),
        *(name for pair in STATE_SUBTRACTIONS.values() for name in pair),
    ]
    model = calculate(
        state_grid_simulation(year, REPAYMENT, DECREASE, STATE_PRIOR_YEAR_TAX),
        year,
        variables,
    )
    # Independent reference: no repayment at all.
    reference = calculate(
        state_grid_simulation(year, zeros, zeros, zeros), year, variables
    )
    out = {}
    for s, state in enumerate(STATE_GRID_STATES):
        rows = slice(s * len(GRID), (s + 1) * len(GRID))
        out[state] = {
            **{name: values[rows] for name, values in model.items()},
            **{
                f"{name}_without_repayment": values[rows]
                for name, values in reference.items()
            },
        }
    return out


@pytest.mark.parametrize("state", sorted(STATE_CREDITS))
def test_state_credit_follows_the_federal_method(state_results, state):
    r = state_results[state]
    credit_applies = r["claim_of_right_credit_applies"]
    assert credit_applies.any() and (eligible() & ~credit_applies).any()
    assert not credit_applies[~eligible()].any()
    credit = r[STATE_CREDITS[state]]
    np.testing.assert_allclose(
        credit, np.where(credit_applies, STATE_PRIOR_YEAR_TAX, 0)
    )
    # Section 1341(b)(3): under the credit method the repayment is not
    # deducted, so the credit is the only change in the state's tax.
    unchanged = credit_applies | ~eligible()
    np.testing.assert_allclose(
        r["state_income_tax"][unchanged],
        (r["state_income_tax_without_repayment"] - credit)[unchanged],
        atol=TOLERANCE,
    )
    refunded = credit_applies & (credit > r["state_income_tax_without_repayment"])
    assert refunded.any(), "the grid should include refunds"
    assert np.all(r["state_income_tax"][refunded] < 0)
    # The other states' credits never reach this state.
    for other in set(STATE_CREDITS) - {state}:
        assert np.all(r[STATE_CREDITS[other]] == 0)


@pytest.mark.parametrize("state", sorted(STATE_SUBTRACTIONS))
def test_state_subtraction_follows_the_federal_method(state_results, state):
    r = state_results[state]
    credit_applies = r["claim_of_right_credit_applies"]
    assert credit_applies.any() and (eligible() & ~credit_applies).any()
    subtraction_name, agi_name = STATE_SUBTRACTIONS[state]
    subtraction = r[subtraction_name]
    np.testing.assert_allclose(subtraction, np.where(credit_applies, REPAYMENT, 0))
    # Louisiana adjusted gross income cannot fall below zero.
    floor = 0 if state == "LA" else -np.inf
    np.testing.assert_allclose(
        r[agi_name],
        np.maximum(r[f"{agi_name}_without_repayment"] - subtraction, floor),
        atol=TOLERANCE,
    )
    unchanged = ~credit_applies & ~eligible()
    np.testing.assert_allclose(
        r["state_income_tax"][unchanged],
        r["state_income_tax_without_repayment"][unchanged],
        atol=TOLERANCE,
    )
    lower = r["state_income_tax"] < r["state_income_tax_without_repayment"] - 1
    assert (credit_applies & lower).any(), "the subtraction should lower some tax"
    assert np.all(
        r["state_income_tax"][credit_applies]
        <= r["state_income_tax_without_repayment"][credit_applies] + TOLERANCE
    )


def state_income_tax(year, repayment, credit_applies=None, state_prior_year_tax=0):
    """State income tax of an itemizing single filer in each state."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, state in enumerate(STATES):
        situation["people"][f"p{i}"] = {
            "age": {year: 40},
            "employment_income": {year: 60_000},
            "charitable_cash_donations": {year: 25_000},
            "claim_of_right_repayment": {year: repayment},
            "claim_of_right_prior_year_tax_decrease": {year: 2_500},
            **{
                name: {year: state_prior_year_tax}
                for name in STATE_PRIOR_YEAR_TAX_INPUTS.values()
            },
        }
        situation["tax_units"][f"t{i}"] = {"members": [f"p{i}"]}
        if credit_applies is not None:
            situation["tax_units"][f"t{i}"]["claim_of_right_credit_applies"] = {
                year: credit_applies
            }
        situation["households"][f"h{i}"] = {
            "members": [f"p{i}"],
            "state_code": {year: state},
        }
    simulation = Simulation(situation=situation)
    return np.asarray(simulation.calculate("state_income_tax", year))


def test_states_follow_section_1341_b_3():
    # One year: each of these three simulations computes every state's tax.
    year = 2025
    without_repayment = state_income_tax(year, 0)
    prior_year_tax = 450
    with_credit = state_income_tax(
        year, 10_000, credit_applies=True, state_prior_year_tax=prior_year_tax
    )
    change = with_credit - without_repayment
    crediting = np.isin(STATES, list(STATE_PRIOR_YEAR_TAX_INPUTS))
    subtracting = np.isin(STATES, list(STATE_SUBTRACTIONS))
    np.testing.assert_allclose(change[~crediting & ~subtracting], 0, atol=TOLERANCE)
    np.testing.assert_allclose(change[crediting], -prior_year_tax, atol=TOLERANCE)
    assert np.all(change[subtracting] < -1), "the subtraction should lower the tax"
    with_deduction = state_income_tax(
        year, 10_000, credit_applies=False, state_prior_year_tax=prior_year_tax
    )
    assert np.any(np.abs(with_deduction - without_repayment) > 1), (
        "the deduction should reach the states that follow federal itemized deductions"
    )
    excluded = np.isin(STATES, STATES_WITHOUT_THE_DEDUCTION)
    np.testing.assert_allclose(
        with_deduction[excluded], without_repayment[excluded], atol=TOLERANCE
    )
