"""Properties of North Carolina's wagering losses itemized deduction.

N.C. Gen. Stat. 105-153.5(a)(2)e, added by S.L. 2026-41 section 44.2 for
taxable years beginning on or after January 1, 2025, allows the wagering
losses allowed under 26 U.S.C. 165(d), to the extent not deducted in arriving
at AGI. The winnings stay in AGI; NCDOR's FAQs (Q38) say they cannot be
reduced by the losses.

Each test evaluates every point of a winnings x losses x charitable deduction
grid in one vectorized simulation per year, so the properties hold for all
grid inputs rather than for a few examples. YAML cases cannot state these
properties:

- the deduction is zero before 2025, never exceeds the winnings or the
  losses, and rises with each;
- it adds to North Carolina itemized deductions one for one, outside the
  $20,000 mortgage and property tax cap;
- with the winnings in AGI, gambling never lowers North Carolina taxable
  income and raises it by at most the winnings, by exactly the net gain for
  a filer who itemizes either way;
- the same holds with the AGI PolicyEngine computes. This last property fails
  until federal gross income counts gambling winnings
  (PolicyEngine/policyengine-us#9637), so it keeps this deduction from
  landing before that fix.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

AMOUNTS = [0, 1, 999, 5_000, 10_000, 12_000, 250_000]
CHARITY = [0, 30_000]
GRID = list(itertools.product(AMOUNTS, AMOUNTS, CHARITY))
SHAPE = (len(AMOUNTS), len(AMOUNTS), len(CHARITY))
WINNINGS, LOSSES, CHARITABLE = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(3)
)
YEARS = [2024, 2025, 2026]
WAGES = 60_000


def grid_simulation(year, gambling, agi=None):
    """One single-person North Carolina tax unit per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            "employment_income": {year: WAGES},
            "real_estate_taxes": {year: 25_000},
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
    """Per year: gambling with the winnings in AGI, no gambling, and gambling
    with the AGI PolicyEngine computes."""
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
def test_deduction_is_bounded_monotone_and_starts_in_2025(results, year):
    deduction = results[year]["with"]["nc_wagering_losses_deduction"]
    if year < 2025:
        assert np.all(deduction == 0)
        return
    assert np.all(deduction >= 0)
    assert np.all(deduction <= WINNINGS + 1e-6)
    assert np.all(deduction <= LOSSES + 1e-6)
    table = deduction.reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) >= -1e-6), "falls as winnings rise"
    assert np.all(np.diff(table, axis=1) >= -1e-6), "falls as losses rise"


@pytest.mark.parametrize("year", YEARS)
def test_deduction_adds_to_itemized_deductions_outside_the_cap(results, year):
    # Real estate taxes of 25,000 already exceed the 20,000 cap.
    with_gambling = results[year]["with"]
    change = (
        with_gambling["nc_itemized_deductions"]
        - (results[year]["without"]["nc_itemized_deductions"])
    )
    np.testing.assert_allclose(
        change, with_gambling["nc_wagering_losses_deduction"], atol=1e-6
    )


@pytest.mark.parametrize("year", YEARS)
def test_gambling_never_lowers_taxable_income_when_winnings_are_in_agi(results, year):
    with_gambling = results[year]["with"]
    change = (
        with_gambling["nc_taxable_income"]
        - results[year]["without"]["nc_taxable_income"]
    )
    assert np.all(change >= -1e-6), "gambling lowered NC taxable income"
    assert np.all(change <= WINNINGS + 1e-6), "taxed more than the winnings"
    itemizes = (
        results[year]["without"]["nc_itemized_deductions"]
        > with_gambling["nc_standard_deduction"]
    )
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
