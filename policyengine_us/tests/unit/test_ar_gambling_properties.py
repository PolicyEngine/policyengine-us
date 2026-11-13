"""Properties of Arkansas's treatment of gambling winnings and losses.

Ark. Code § 26-51-424(a)(2)(B), as amended by Act 155 of 2017, § 21, from
2015: gambling losses are deductible to the extent of gambling winnings and
are not subject to the 2% floor on miscellaneous itemized deductions. The
winnings are Arkansas gross income (other income, Form AR-OI).

Each test evaluates every point of a winnings x losses grid in one vectorized
simulation, so the properties hold for all grid inputs rather than for a few
examples:

- the deduction equals min(losses, winnings) summed over the tax unit;
- it is non-negative, never exceeds winnings or losses, and rises with each;
- it does not depend on Arkansas AGI (no 2% floor) or on the year;
- it agrees with the federal wagering losses deduction, which applies the
  same rule under 26 U.S.C. § 165(d) through 2025;
- gambling never lowers Arkansas taxable income, and raises it by at most
  the winnings; for a filer who itemizes either way, it raises it by exactly
  max(0, winnings - losses).
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

AMOUNTS = [0, 1, 999, 1_000, 2_200, 5_000, 10_000, 250_000]
GRID = list(itertools.product(AMOUNTS, AMOUNTS))
WINNINGS = np.array([g[0] for g in GRID], dtype=float)
LOSSES = np.array([g[1] for g in GRID], dtype=float)
YEARS = [2015, 2017, 2018, 2019, 2020, 2022, 2025]


def grid_simulation(year, person_inputs, tax_unit_inputs=None):
    """One single-person Arkansas tax unit per grid point."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(len(GRID)):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {year: 40},
            **{
                name: {year: float(values[i])} for name, values in person_inputs.items()
            },
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            **{
                name: {year: float(values[i])}
                for name, values in (tax_unit_inputs or {}).items()
            },
        }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "AR"},
        }
    return Simulation(situation=situation)


def constant(value):
    return np.full(len(GRID), value, dtype=float)


def as_table(values):
    """Rows index winnings, columns index losses."""
    return np.asarray(values).reshape(len(AMOUNTS), len(AMOUNTS))


@pytest.mark.parametrize("year", YEARS)
def test_deduction_is_losses_capped_at_winnings(year):
    sim = grid_simulation(
        year, {"gambling_winnings": WINNINGS, "gambling_losses": LOSSES}
    )
    deduction = sim.calculate("ar_gambling_loss_deduction", year)
    np.testing.assert_allclose(deduction, np.minimum(LOSSES, WINNINGS))
    assert np.all(deduction >= 0)
    assert np.all(deduction <= WINNINGS)
    assert np.all(deduction <= LOSSES)
    table = as_table(deduction)
    assert np.all(np.diff(table, axis=0) >= 0), "falls as winnings rise"
    assert np.all(np.diff(table, axis=1) >= 0), "falls as losses rise"


def test_deduction_does_not_depend_on_the_year():
    results = []
    for year in YEARS:
        sim = grid_simulation(
            year, {"gambling_winnings": WINNINGS, "gambling_losses": LOSSES}
        )
        results.append(sim.calculate("ar_gambling_loss_deduction", year))
    for result in results[1:]:
        np.testing.assert_array_equal(result, results[0])


@pytest.mark.parametrize("agi", [0, 50_000, 1_000_000])
def test_deduction_is_not_subject_to_the_two_percent_floor(agi):
    year = 2019
    sim = grid_simulation(
        year,
        {
            "gambling_winnings": WINNINGS,
            "gambling_losses": LOSSES,
            "ar_agi_joint": constant(agi),
            "ar_agi_indiv": constant(agi),
        },
    )
    deduction = sim.calculate("ar_gambling_loss_deduction", year)
    np.testing.assert_allclose(deduction, np.minimum(LOSSES, WINNINGS))
    # No other itemized deduction has inputs, so the itemized total is the
    # full gambling deduction whatever the AGI.
    itemized = sim.calculate("ar_itemized_deductions_joint", year)
    np.testing.assert_allclose(itemized, deduction)


@pytest.mark.parametrize("year", YEARS)
def test_deduction_matches_the_federal_wagering_losses_deduction(year):
    # 26 U.S.C. § 165(d) allows wagering losses only to the extent of wagering
    # gains through 2025, the same cap Arkansas applies.
    sim = grid_simulation(
        year, {"gambling_winnings": WINNINGS, "gambling_losses": LOSSES}
    )
    np.testing.assert_allclose(
        sim.calculate("ar_gambling_loss_deduction", year),
        sim.calculate("wagering_losses_deduction", year),
    )


def taxable_income(year, winnings, losses, other_itemized):
    sim = grid_simulation(
        year,
        {
            "irs_employment_income": constant(60_000),
            "gambling_winnings": winnings,
            "gambling_losses": losses,
        },
        {"ar_medical_expense_deduction_joint": constant(other_itemized)},
    )
    return sim.calculate("ar_taxable_income_joint", year)


@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("other_itemized", [0, 20_000])
def test_gambling_never_lowers_arkansas_taxable_income(year, other_itemized):
    with_gambling = taxable_income(year, WINNINGS, LOSSES, other_itemized)
    without_gambling = taxable_income(year, constant(0), constant(0), other_itemized)
    change = with_gambling - without_gambling
    assert np.all(change >= -1e-6), "gambling lowered taxable income"
    assert np.all(change <= WINNINGS + 1e-6), "taxed more than the winnings"
    if other_itemized:
        # Itemized deductions exceed the standard deduction with or without
        # gambling, so only net winnings are taxed.
        np.testing.assert_allclose(change, np.maximum(0, WINNINGS - LOSSES))
