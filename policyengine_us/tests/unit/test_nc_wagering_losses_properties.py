"""Properties of North Carolina's wagering losses itemized deduction.

N.C. Gen. Stat. 105-153.5(a)(2)e, added by S.L. 2026-41 section 44.2 for
taxable years beginning on or after January 1, 2025, allows the wagering
losses allowed under 26 U.S.C. 165(d), to the extent not deducted in arriving
at AGI. The winnings stay in AGI; NCDOR's FAQs (Q38) say they cannot be
reduced by the losses. North Carolina's Code is the Internal Revenue Code as
of July 5, 2025 (S.L. 2026-31 section 12.(a)), so P.L. 119-21 section 70114
limits the deduction to 90% of losses from 2026.

YAML cases check single households. These tests check properties at every
point of a winnings x losses x charitable deduction x property tax grid,
using three vectorized simulations per year (with the winnings in AGI,
without gambling, and with the AGI PolicyEngine computes):

- the deduction is zero before 2025 and equals the section 165(d) amount,
  min(share x losses, winnings), with share 1 in 2025 and 0.9 from 2026;
- it never exceeds the winnings or the losses and rises with each;
- it adds to North Carolina itemized deductions one for one, including when
  property taxes already exceed the $20,000 mortgage and property tax cap;
- with the winnings in AGI, gambling never lowers North Carolina taxable
  income and raises it by at most the winnings, by exactly the net gain for
  a filer who itemizes either way;
- the same holds with the AGI PolicyEngine computes.

Until PolicyEngine/policyengine-us#9637 is fixed (federal gross income leaves
out gambling winnings, and the federal deduction has no 90% share), the 2026
section 165(d) check and the modeled-AGI check fail. They keep this deduction
from landing before that fix.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

AMOUNTS = [0, 1, 999, 5_000, 10_000, 12_000, 250_000]
CHARITY = [0, 30_000]
PROPERTY_TAX = [0, 25_000]
AXES = [AMOUNTS, AMOUNTS, CHARITY, PROPERTY_TAX]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
WINNINGS, LOSSES, CHARITABLE, PROPERTY = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(len(AXES))
)
YEARS = [2024, 2025, 2026]
# Share of wagering losses section 165(d) allows (P.L. 119-21 section 70114).
LOSS_SHARE = {2025: 1.0, 2026: 0.9}
WAGES = 60_000


def grid_simulation(year, gambling, agi=None):
    """One single-person North Carolina tax unit per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            "employment_income": {year: WAGES},
            "real_estate_taxes": {year: PROPERTY[i]},
            "gambling_winnings": {year: WINNINGS[i] if gambling else 0},
            "gambling_losses": {year: LOSSES[i] if gambling else 0},
        }
        tax_unit = {
            "members": [person],
            "charitable_deduction": {year: CHARITABLE[i]},
        }
        if agi is not None:
            tax_unit["adjusted_gross_income"] = {year: float(agi[i])}
        situation["tax_units"][f"t{i}"] = tax_unit
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "NC"},
        }
    return Simulation(situation=situation)


def calculate(sim, year):
    return {
        variable: np.asarray(sim.calculate(variable, year))
        for variable in [
            "nc_wagering_losses_deduction",
            "nc_itemized_deductions",
            "nc_standard_deduction",
            "nc_taxable_income",
        ]
    }


@pytest.fixture(scope="module")
def results():
    out = {}
    for year in YEARS:
        out[year] = {
            "with": calculate(grid_simulation(year, True, agi=WAGES + WINNINGS), year),
            "without": calculate(
                grid_simulation(year, False, agi=np.full(len(GRID), WAGES)),
                year,
            ),
            "modeled": calculate(grid_simulation(year, True), year),
        }
    return out


@pytest.mark.parametrize("year", YEARS)
def test_deduction_is_the_section_165d_amount_from_2025(results, year):
    deduction = results[year]["with"]["nc_wagering_losses_deduction"]
    if year < 2025:
        assert np.all(deduction == 0)
        return
    np.testing.assert_allclose(
        deduction, np.minimum(LOSS_SHARE[year] * LOSSES, WINNINGS), atol=1e-6
    )


@pytest.mark.parametrize("year", [2025, 2026])
def test_deduction_is_bounded_and_monotone(results, year):
    deduction = results[year]["with"]["nc_wagering_losses_deduction"]
    assert np.all(deduction >= 0)
    assert np.all(deduction <= WINNINGS + 1e-6)
    assert np.all(deduction <= LOSSES + 1e-6)
    table = deduction.reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) >= -1e-6), "falls as winnings rise"
    assert np.all(np.diff(table, axis=1) >= -1e-6), "falls as losses rise"


@pytest.mark.parametrize("year", YEARS)
def test_deduction_adds_to_itemized_deductions_outside_the_cap(results, year):
    with_gambling = results[year]["with"]
    change = (
        with_gambling["nc_itemized_deductions"]
        - results[year]["without"]["nc_itemized_deductions"]
    )
    np.testing.assert_allclose(
        change, with_gambling["nc_wagering_losses_deduction"], atol=1e-6
    )


@pytest.mark.parametrize("year", YEARS)
def test_gambling_never_lowers_taxable_income_when_winnings_are_in_agi(results, year):
    with_gambling = results[year]["with"]
    without = results[year]["without"]
    change = with_gambling["nc_taxable_income"] - without["nc_taxable_income"]
    assert np.all(change >= -1e-6), "gambling lowered NC taxable income"
    assert np.all(change <= WINNINGS + 1e-6), "taxed more than the winnings"
    itemizes = without["nc_itemized_deductions"] > without["nc_standard_deduction"]
    assert itemizes.any() and not itemizes.all()
    net_gain = WINNINGS - with_gambling["nc_wagering_losses_deduction"]
    np.testing.assert_allclose(change[itemizes], net_gain[itemizes], atol=1e-6)


@pytest.mark.parametrize("year", [2025, 2026])
def test_gambling_never_lowers_taxable_income_with_modeled_agi(results, year):
    # Fails until federal gross income counts gambling winnings
    # (PolicyEngine/policyengine-us#9637): PolicyEngine's AGI leaves them out
    # while this deduction subtracts the losses.
    change = (
        results[year]["modeled"]["nc_taxable_income"]
        - results[year]["without"]["nc_taxable_income"]
    )
    assert np.all(change >= -1e-6), "gambling lowered NC taxable income"
