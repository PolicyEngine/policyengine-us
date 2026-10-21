"""Properties of North Carolina's claim of right repayment deduction.

N.C. Gen. Stat. 105-153.5(a)(2)d, added by S.L. 2016-5 for 2014 and later: a
repayment of $3,000 or less is deductible less (i) the section 67(a) floor,
two percent of federal AGI, minus (ii) the other miscellaneous itemized
deductions, not below zero; a larger repayment is deductible in full. From
2026 (S.L. 2026-31 section 1.8) only repayments of amounts included in AGI as
modified for North Carolina count.

YAML cases check single households. These tests check properties at every
point of a grid, one vectorized simulation per year, and compare the model
with independent line-by-line implementations of NCDOR's worksheets. A YAML
case cannot state a property that holds for all inputs, such as monotonicity
across the $3,000 threshold:

- the deduction matches the 2016 Repayment of Claim of Right Worksheet,
  which subtracts other miscellaneous deductions from the floor, and the
  2025 worksheet, which subtracts the whole floor because section 67(g)
  disallows those deductions from 2018;
- it is non-negative, never exceeds the repayment, rises with the repayment
  (also across the $3,000 threshold) and falls as AGI rises;
- it adds to North Carolina itemized deductions one for one, including when
  property taxes already exceed the $20,000 mortgage and property tax cap,
  and never raises North Carolina income tax, including when the repayment
  moves the filer from the standard deduction to itemizing;
- from 2026 it is the 2025 worksheet applied to the part of the repayment
  North Carolina taxed when received; before 2026 that split has no effect.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

REPAYMENTS = [0, 1, 999, 1_000, 2_999, 3_000, 3_000.5, 3_001, 10_000, 250_000]
AGIS = [-5_000, 0, 50_000, 100_000, 150_000, 1_000_000]
OTHER_MISC = [0, 600, 5_000]
CHARITY = [0, 20_000]
PROPERTY_TAX = [0, 25_000]
AXES = [REPAYMENTS, AGIS, OTHER_MISC, CHARITY, PROPERTY_TAX]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
REPAYMENT, AGI, MISC, CHARITABLE, PROPERTY = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(len(AXES))
)
# 2026 grid: repayment x share of it North Carolina excluded when received x AGI.
SHARES = [0, 0.25, 0.75, 1]
GRID_2026 = list(itertools.product(REPAYMENTS, SHARES, AGIS))
REPAYMENT_2026, SHARE_2026, AGI_2026 = (
    np.array([point[i] for point in GRID_2026], dtype=float) for i in range(3)
)


def grid_simulation(year, people, tax_units):
    """One single-person North Carolina tax unit per grid point."""
    size = len(next(iter(people.values())))
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(size):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            **{name: {year: float(values[i])} for name, values in people.items()},
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            **{name: {year: float(values[i])} for name, values in tax_units.items()},
        }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "NC"},
        }
    return Simulation(situation=situation)


def worksheet_2016(repayment, agi, other_misc):
    """2016 Form D-401 instructions, PDF p. 13, lines 1-6."""
    line1 = repayment
    line2 = 0.02 * np.maximum(agi, 0)  # federal Schedule A line 26
    line3 = other_misc + repayment  # federal Schedule A line 24
    line4 = line3 - line1
    line5 = np.maximum(line2 - line4, 0)
    line6 = np.maximum(line1 - line5, 0)
    return np.where(repayment > 3_000, repayment, line6)


def worksheet_2025(repayment, agi):
    """2025 Form D-401 instructions, PDF p. 20, lines 1-4."""
    line3 = np.maximum(0.02 * agi, 0)
    line4 = np.maximum(repayment - line3, 0)
    return np.where(repayment > 3_000, repayment, line4)


@pytest.fixture(scope="module")
def results():
    out = {}
    for year in [2016, 2025]:
        sim = grid_simulation(
            year,
            {
                "claim_of_right_repayment": REPAYMENT,
                "unreimbursed_business_employee_expenses": MISC,
                "real_estate_taxes": PROPERTY,
            },
            {"adjusted_gross_income": AGI, "charitable_deduction": CHARITABLE},
        )
        out[year] = {
            variable: np.asarray(sim.calculate(variable, year))
            for variable in [
                "nc_claim_of_right_deduction",
                "nc_itemized_deductions",
                "nc_income_tax",
            ]
        }
    return out


def test_deduction_matches_the_worksheets(results):
    np.testing.assert_allclose(
        results[2016]["nc_claim_of_right_deduction"],
        worksheet_2016(REPAYMENT, AGI, MISC),
        atol=1e-6,
    )
    np.testing.assert_allclose(
        results[2025]["nc_claim_of_right_deduction"],
        worksheet_2025(REPAYMENT, AGI),
        atol=1e-6,
    )


@pytest.mark.parametrize("year", [2016, 2025])
def test_deduction_is_bounded_and_monotone(results, year):
    deduction = results[year]["nc_claim_of_right_deduction"]
    assert np.all(deduction >= 0)
    assert np.all(deduction <= REPAYMENT + 1e-6)
    above = REPAYMENT > 3_000
    np.testing.assert_allclose(deduction[above], REPAYMENT[above])
    table = deduction.reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) >= -1e-6), "falls as the repayment rises"
    assert np.all(np.diff(table, axis=1) <= 1e-6), "rises as AGI rises"
    assert np.all(np.diff(table, axis=2) >= -1e-6), "falls as other expenses rise"


def test_other_miscellaneous_expenses_matter_only_before_2018(results):
    for year, matters in [(2016, True), (2025, False)]:
        table = results[year]["nc_claim_of_right_deduction"].reshape(SHAPE)
        spread = np.abs(table - table[:, :, :1]).max()
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


def test_from_2026_only_the_part_north_carolina_taxed_counts():
    excluded = SHARE_2026 * REPAYMENT_2026
    deductions = {}
    for year in [2025, 2026]:
        sim = grid_simulation(
            year,
            {
                "claim_of_right_repayment": REPAYMENT_2026,
                "nc_claim_of_right_repayment_excluded_from_income": excluded,
            },
            {"adjusted_gross_income": AGI_2026},
        )
        deductions[year] = np.asarray(
            sim.calculate("nc_claim_of_right_deduction", year)
        )
    np.testing.assert_allclose(
        deductions[2025], worksheet_2025(REPAYMENT_2026, AGI_2026), atol=1e-6
    )
    np.testing.assert_allclose(
        deductions[2026],
        worksheet_2025(REPAYMENT_2026 - excluded, AGI_2026),
        atol=1e-6,
    )
    assert np.all(deductions[2026] <= deductions[2025] + 1e-6)
