"""Properties of Wisconsin's claim of right credit and subtraction.

A Wisconsin filer who repays more than $3,000 of income taxed in an earlier
year may either subtract the repayment from income (Wis. Stat.
71.05(6)(b)29) or take a refundable credit for the decrease in the earlier
year's Wisconsin tax (Wis. Stat. 71.07(1)), not both. The model takes the
option with less Wisconsin income tax, and the subtraction when they are
equal to the cent. The choice does not depend on the method 26 U.S.C. 1341 applies to
the federal return.

YAML cases check single households by hand. These tests check properties at
every point of a grid, one vectorized simulation per year and scenario, and
compare the model's branch computations with independent simulations that
fix the Wisconsin choice as an input:

- the lesser-of rule: Wisconsin income tax equals the smaller of the tax with
  the subtraction fixed and the tax with no repayment at all less the
  prior-year decrease, ties going to the subtraction;
- the branches agree with those independent simulations;
- the subtraction is the whole repayment or nothing, the credit is the whole
  decrease or nothing, and never both;
- a repayment of $3,000 or less changes nothing;
- the relief never raises tax, and tax never rises with the repayment (also
  across the $3,000 threshold) or with the prior-year decrease;
- a credit above the year's tax is paid to the filer;
- the federal method changes nothing in Wisconsin.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

REPAYMENTS = [0, 2_999, 3_000, 3_001, 5_000, 20_000, 150_000]
DECREASES = [0, 150, 1_100, 9_000]
WAGES = [0, 15_000, 60_000, 200_000, 1_000_000]
INTEREST = [0, 30_000]
AXES = [REPAYMENTS, DECREASES, WAGES, INTEREST]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
REPAYMENT, DECREASE, WAGE, INTEREST_PAID = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(len(AXES))
)
# An illustrative decrease in the earlier year's federal tax, large enough
# that the federal method varies across the grid.
FEDERAL_DECREASE = 0.2 * REPAYMENT
THRESHOLD = 3_000
YEARS = [2025, 2026]
TOLERANCE = 0.01
VARIABLES = [
    "wi_income_tax",
    "wi_claim_of_right_eligible",
    "wi_claim_of_right_credit_applies",
    "wi_claim_of_right_subtraction",
    "wi_claim_of_right_credit",
    "claim_of_right_credit_applies",
]


def grid_simulation(year, repayment, decrease, tax_units=None):
    """One single-person Wisconsin tax unit per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            "employment_income": {year: WAGE[i]},
            "claim_of_right_repayment": {year: float(repayment[i])},
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            "claim_of_right_prior_year_tax_decrease": {year: FEDERAL_DECREASE[i]},
            "wi_claim_of_right_prior_year_tax_decrease": {year: float(decrease[i])},
            "interest_deduction": {year: INTEREST_PAID[i]},
            **{name: {year: value} for name, value in (tax_units or {}).items()},
        }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "WI"},
        }
    return Simulation(situation=situation)


def calculate(simulation, year, variables):
    return {v: np.asarray(simulation.calculate(v, year)) for v in variables}


@pytest.fixture(scope="module")
def results():
    zeros = np.zeros_like(REPAYMENT)
    out = {}
    for year in YEARS:
        model = grid_simulation(year, REPAYMENT, DECREASE)
        out[year] = calculate(
            model,
            year,
            VARIABLES
            + [
                "wi_income_tax_if_claiming_claim_of_right_subtraction",
                "wi_income_tax_if_claiming_claim_of_right_credit",
            ],
        )

        def wisconsin_tax(repayment, decrease, **tax_units):
            simulation = grid_simulation(year, repayment, decrease, tax_units)
            return np.asarray(simulation.calculate("wi_income_tax", year))

        # Independent references: no repayment at all, and each Wisconsin
        # option fixed as an input rather than chosen in a branch.
        out[year]["tax_without_repayment"] = wisconsin_tax(zeros, zeros)
        out[year]["tax_with_subtraction"] = wisconsin_tax(
            REPAYMENT, DECREASE, wi_claim_of_right_credit_applies=False
        )
        out[year]["tax_with_credit"] = wisconsin_tax(
            REPAYMENT, DECREASE, wi_claim_of_right_credit_applies=True
        )
        # The model's own choice under each federal method.
        out[year]["tax_under_federal_deduction"] = wisconsin_tax(
            REPAYMENT, DECREASE, claim_of_right_credit_applies=False
        )
        out[year]["tax_under_federal_credit"] = wisconsin_tax(
            REPAYMENT, DECREASE, claim_of_right_credit_applies=True
        )
    return out


def eligible():
    return REPAYMENT > THRESHOLD


@pytest.mark.parametrize("year", YEARS)
def test_tax_is_the_lesser_of_the_two_options(results, year):
    r = results[year]
    tax_with_subtraction = r["tax_with_subtraction"]
    tax_with_credit = r["tax_without_repayment"] - DECREASE
    credit = eligible() & (
        np.round(tax_with_credit, 2) < np.round(tax_with_subtraction, 2)
    )
    assert credit.any() and (eligible() & ~credit).any(), "both options occur"
    np.testing.assert_array_equal(r["wi_claim_of_right_credit_applies"], credit)
    expected = np.where(
        eligible(),
        np.where(credit, tax_with_credit, tax_with_subtraction),
        r["tax_without_repayment"],
    )
    np.testing.assert_allclose(r["wi_income_tax"], expected, atol=TOLERANCE)


@pytest.mark.parametrize("year", YEARS)
def test_branches_match_independent_simulations(results, year):
    r = results[year]
    np.testing.assert_allclose(
        r["wi_income_tax_if_claiming_claim_of_right_subtraction"][eligible()],
        r["tax_with_subtraction"][eligible()],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        r["wi_income_tax_if_claiming_claim_of_right_credit"][eligible()],
        r["tax_with_credit"][eligible()],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        r["tax_with_credit"][eligible()],
        (r["tax_without_repayment"] - DECREASE)[eligible()],
        atol=TOLERANCE,
    )


@pytest.mark.parametrize("year", YEARS)
def test_subtraction_and_credit_are_all_or_nothing_and_exclusive(results, year):
    r = results[year]
    credit_applies = r["wi_claim_of_right_credit_applies"]
    subtraction = r["wi_claim_of_right_subtraction"]
    credit = r["wi_claim_of_right_credit"]
    np.testing.assert_array_equal(r["wi_claim_of_right_eligible"], eligible())
    np.testing.assert_allclose(
        subtraction, np.where(eligible() & ~credit_applies, REPAYMENT, 0)
    )
    np.testing.assert_allclose(credit, np.where(credit_applies, DECREASE, 0))
    assert not np.any((subtraction > 0) & (credit > 0))


@pytest.mark.parametrize("year", YEARS)
def test_a_repayment_of_3000_or_less_changes_nothing(results, year):
    r = results[year]
    small = ~eligible()
    assert not r["wi_claim_of_right_credit_applies"][small].any()
    np.testing.assert_allclose(
        r["wi_income_tax"][small], r["tax_without_repayment"][small], atol=TOLERANCE
    )


@pytest.mark.parametrize("year", YEARS)
def test_tax_never_rises(results, year):
    r = results[year]
    assert np.all(r["wi_income_tax"] <= r["tax_without_repayment"] + TOLERANCE)
    table = r["wi_income_tax"].reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) <= TOLERANCE), "rises with the repayment"
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises with the decrease"


@pytest.mark.parametrize("year", YEARS)
def test_a_credit_above_the_tax_is_paid_to_the_filer(results, year):
    r = results[year]
    credit_applies = r["wi_claim_of_right_credit_applies"]
    refunded = credit_applies & (DECREASE > r["tax_without_repayment"] + TOLERANCE)
    assert refunded.any(), "the grid should include refunds"
    assert np.all(r["wi_income_tax"][refunded] < 0)


@pytest.mark.parametrize("year", YEARS)
def test_the_federal_method_changes_nothing_in_wisconsin(results, year):
    r = results[year]
    assert r["claim_of_right_credit_applies"].any(), "the federal credit occurs"
    assert (eligible() & ~r["claim_of_right_credit_applies"]).any()
    for federal in ("tax_under_federal_deduction", "tax_under_federal_credit"):
        np.testing.assert_allclose(r[federal], r["wi_income_tax"], atol=TOLERANCE)
