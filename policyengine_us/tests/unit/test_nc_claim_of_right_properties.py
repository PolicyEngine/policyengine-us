"""Properties of North Carolina's claim of right repayment deduction.

N.C. Gen. Stat. 105-153.5(a)(2)d, added by S.L. 2016-5 for 2014 and later: a
repayment of $3,000 or less is deductible less (i) the section 67(a) floor,
two percent of federal AGI, minus (ii) the other miscellaneous itemized
deductions, not below zero; a larger repayment is deductible in full.

Each test evaluates every point of a repayment x AGI x other miscellaneous
expenses x charitable deduction grid in one vectorized simulation, so the
properties hold for all grid inputs rather than for a few examples. YAML
cases cannot state these properties:

- the deduction matches the line-by-line arithmetic of NCDOR's Repayment of
  Claim of Right Worksheet: the 2016 version, which subtracts other
  miscellaneous deductions from the floor, and the 2025 version, which
  subtracts the whole floor because section 67(g) disallows those
  deductions from 2018;
- it is non-negative, never exceeds the repayment, rises with the repayment
  (also across the $3,000 threshold) and falls as AGI rises;
- it adds to North Carolina itemized deductions one for one, outside the
  $20,000 mortgage and property tax cap, and never raises North Carolina
  income tax.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

REPAYMENTS = [0, 1, 999, 1_000, 2_999, 3_000, 3_000.5, 3_001, 10_000, 250_000]
AGIS = [-5_000, 0, 50_000, 100_000, 150_000, 1_000_000]
OTHER_MISC = [0, 600, 5_000]
CHARITY = [0, 20_000]
GRID = list(itertools.product(REPAYMENTS, AGIS, OTHER_MISC, CHARITY))
SHAPE = (len(REPAYMENTS), len(AGIS), len(OTHER_MISC), len(CHARITY))
REPAYMENT, AGI, MISC, CHARITABLE = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(4)
)


def grid_simulation(year):
    """One single-person North Carolina tax unit per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            "claim_of_right_repayment": {year: REPAYMENT[i]},
            "unreimbursed_business_employee_expenses": {year: MISC[i]},
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            "adjusted_gross_income": {year: AGI[i]},
            "charitable_deduction": {year: CHARITABLE[i]},
        }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "NC"},
        }
    return Simulation(situation=situation)


def worksheet_2016():
    """2016 Form D-401 instructions, PDF p. 13, lines 1-6."""
    line1 = REPAYMENT
    line2 = 0.02 * np.maximum(AGI, 0)  # federal Schedule A line 26
    line3 = MISC + REPAYMENT  # federal Schedule A line 24
    line4 = line3 - line1
    line5 = np.maximum(line2 - line4, 0)
    line6 = np.maximum(line1 - line5, 0)
    return np.where(REPAYMENT > 3_000, REPAYMENT, line6)


def worksheet_2025():
    """2025 Form D-401 instructions, PDF p. 20, lines 1-4."""
    line3 = np.maximum(0.02 * AGI, 0)
    line4 = np.maximum(REPAYMENT - line3, 0)
    return np.where(REPAYMENT > 3_000, REPAYMENT, line4)


@pytest.fixture(scope="module")
def results():
    out = {}
    for year in [2016, 2025]:
        sim = grid_simulation(year)
        out[year] = {
            variable: np.asarray(sim.calculate(variable, year))
            for variable in [
                "nc_claim_of_right_deduction",
                "nc_itemized_deductions",
                "nc_income_tax",
            ]
        }
    return out


@pytest.mark.parametrize(
    "year, worksheet", [(2016, worksheet_2016), (2025, worksheet_2025)]
)
def test_deduction_matches_the_worksheet(results, year, worksheet):
    np.testing.assert_allclose(
        results[year]["nc_claim_of_right_deduction"], worksheet(), atol=1e-6
    )


@pytest.mark.parametrize("year", [2016, 2025])
def test_deduction_is_bounded_and_monotone(results, year):
    deduction = results[year]["nc_claim_of_right_deduction"]
    assert np.all(deduction >= 0)
    assert np.all(deduction <= REPAYMENT + 1e-6)
    np.testing.assert_allclose(
        deduction[REPAYMENT > 3_000], REPAYMENT[REPAYMENT > 3_000]
    )
    table = deduction.reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) >= -1e-6), "falls as the repayment rises"
    assert np.all(np.diff(table, axis=1) <= 1e-6), "rises as AGI rises"
    assert np.all(np.diff(table, axis=2) >= -1e-6), "falls as other expenses rise"


def test_other_miscellaneous_expenses_matter_only_before_2018(results):
    for year, matters in [(2016, True), (2025, False)]:
        table = results[year]["nc_claim_of_right_deduction"].reshape(SHAPE)
        spread = np.abs(table - table[:, :, :1, :]).max()
        assert (spread > 0) == matters, year


@pytest.mark.parametrize("year", [2016, 2025])
def test_deduction_adds_to_itemized_deductions_and_never_raises_tax(results, year):
    deduction = results[year]["nc_claim_of_right_deduction"].reshape(SHAPE)
    itemized = results[year]["nc_itemized_deductions"].reshape(SHAPE)
    tax = results[year]["nc_income_tax"].reshape(SHAPE)
    # Row 0 of the repayment axis is the same tax unit with no repayment.
    np.testing.assert_allclose(itemized - itemized[:1], deduction, atol=1e-6)
    assert np.all(tax <= tax[:1] + 1e-6), "a repayment raised North Carolina tax"
    assert np.all(np.diff(tax, axis=0) <= 1e-6), "tax rises with the repayment"
