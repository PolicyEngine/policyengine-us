"""Properties of Hawaii's claim of right deduction and credit.

From 2022 section 1341 is operative in Hawaii (Act 56, SLH 2023): Hawaii tax is
the lesser of the tax with a deduction for a repayment over $3,000 and the tax
without it less the decrease in prior-year Hawaii tax (Form N-364), a
refundable credit. Otherwise a repayment is a miscellaneous itemized deduction
above 2% of Hawaii AGI while Hawaii allows those (through 2025). The policy
cases are in YAML. Hawaii picks the method by computing Hawaii tax in two
override branches, so these tests compare the model with independent
simulations that fix the method as an input, over a grid for 2021, 2025 and
2026:

- the lesser-of rule: Hawaii income tax equals the smaller of the tax with the
  deduction method fixed and the tax with the credit method fixed, ties going
  to the deduction, and the branches equal those simulations;
- the deduction is the whole repayment or nothing and the credit is the whole
  decrease or nothing when section 1341 applies, never both; before 2022 there
  is never a credit;
- Hawaii tax does not depend on the federal method, never rises with a
  repayment, and never rises as the repayment or the prior-year decrease grows.
"""

import gc
import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = [2021, 2025, 2026]
REPAYMENTS = [0, 2_000, 3_000, 3_001, 10_000, 60_000]
DECREASES = [0, 300, 3_000]
WAGES = [30_000, 100_000, 400_000]
CHARITY = [0, 30_000]
AXES = [REPAYMENTS, DECREASES, WAGES, CHARITY]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
REPAYMENT, DECREASE, WAGE, CHARITABLE = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(len(AXES))
)
ZEROS = np.zeros_like(REPAYMENT)
THRESHOLD = 3_000
TOLERANCE = 0.01


def grid_simulation(year, repayment=REPAYMENT, tax_unit_inputs=None):
    """One single Hawaii filer per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            "employment_income": {year: WAGE[i]},
            "charitable_cash_donations": {year: CHARITABLE[i]},
            "claim_of_right_repayment": {year: float(repayment[i])},
        }
        tax_unit = {
            "members": [person],
            "hi_claim_of_right_prior_year_tax_decrease": {year: float(DECREASE[i])},
            "claim_of_right_prior_year_tax_decrease": {year: float(DECREASE[i])},
        }
        for name, value in (tax_unit_inputs or {}).items():
            tax_unit[name] = {year: value}
        situation["tax_units"][f"t{i}"] = tax_unit
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "HI"},
        }
    return Simulation(situation=situation)


def calculate(simulation, year, variables):
    return {v: np.asarray(simulation.calculate(v, year)) for v in variables}


@pytest.fixture(scope="module")
def results():
    out = {}
    for year in YEARS:
        r = calculate(
            grid_simulation(year),
            year,
            [
                "hi_income_tax",
                "hi_claim_of_right_section_1341_eligible",
                "hi_claim_of_right_credit_applies",
                "hi_claim_of_right_deduction",
                "hi_claim_of_right_credit",
                "hi_income_tax_if_claiming_claim_of_right_credit",
                "hi_income_tax_if_claiming_claim_of_right_deduction",
            ],
        )
        r["tax_with_credit"] = calculate(
            grid_simulation(
                year, tax_unit_inputs={"hi_claim_of_right_credit_applies": True}
            ),
            year,
            ["hi_income_tax"],
        )["hi_income_tax"]
        r["tax_with_deduction"] = calculate(
            grid_simulation(
                year, tax_unit_inputs={"hi_claim_of_right_credit_applies": False}
            ),
            year,
            ["hi_income_tax"],
        )["hi_income_tax"]
        r["tax_without_repayment"] = calculate(
            grid_simulation(year, ZEROS), year, ["hi_income_tax"]
        )["hi_income_tax"]
        r["tax_federal_credit"] = calculate(
            grid_simulation(
                year, tax_unit_inputs={"claim_of_right_credit_applies": True}
            ),
            year,
            ["hi_income_tax"],
        )["hi_income_tax"]
        out[year] = r
    yield out
    gc.collect()


@pytest.mark.parametrize("year", YEARS)
def test_tax_is_the_lesser_of_the_two_methods(results, year):
    r = results[year]
    eligible = r["hi_claim_of_right_section_1341_eligible"]
    np.testing.assert_array_equal(eligible, (REPAYMENT > THRESHOLD) & (year >= 2022))
    credit = eligible & (
        np.round(r["tax_with_credit"], 2) < np.round(r["tax_with_deduction"], 2)
    )
    np.testing.assert_array_equal(r["hi_claim_of_right_credit_applies"], credit)
    expected = np.where(credit, r["tax_with_credit"], r["tax_with_deduction"])
    np.testing.assert_allclose(r["hi_income_tax"], expected, atol=TOLERANCE)
    if year >= 2022:
        assert credit.any() and (eligible & ~credit).any(), "both methods occur"


@pytest.mark.parametrize("year", [2025, 2026])
def test_branches_match_independent_simulations(results, year):
    r = results[year]
    eligible = r["hi_claim_of_right_section_1341_eligible"]
    np.testing.assert_allclose(
        r["hi_income_tax_if_claiming_claim_of_right_credit"][eligible],
        r["tax_with_credit"][eligible],
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        r["hi_income_tax_if_claiming_claim_of_right_deduction"][eligible],
        r["tax_with_deduction"][eligible],
        atol=TOLERANCE,
    )


@pytest.mark.parametrize("year", YEARS)
def test_deduction_and_credit_are_exclusive(results, year):
    r = results[year]
    eligible = r["hi_claim_of_right_section_1341_eligible"]
    credit_applies = r["hi_claim_of_right_credit_applies"]
    deduction, credit = r["hi_claim_of_right_deduction"], r["hi_claim_of_right_credit"]
    np.testing.assert_allclose(
        deduction[eligible & ~credit_applies], REPAYMENT[eligible & ~credit_applies]
    )
    np.testing.assert_allclose(deduction[credit_applies], 0)
    np.testing.assert_allclose(credit, np.where(credit_applies, DECREASE, 0))
    assert not np.any((deduction > 0) & (credit > 0))
    assert np.all(deduction <= REPAYMENT + TOLERANCE)
    if year < 2022:
        assert not credit_applies.any() and np.all(credit == 0)


@pytest.mark.parametrize("year", YEARS)
def test_tax_ignores_the_federal_method_and_never_rises(results, year):
    r = results[year]
    np.testing.assert_allclose(
        r["tax_federal_credit"], r["hi_income_tax"], atol=TOLERANCE
    )
    assert np.all(r["hi_income_tax"] <= r["tax_without_repayment"] + TOLERANCE)
    table = r["hi_income_tax"].reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) <= TOLERANCE), "rises with the repayment"
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises with the decrease"
