"""Properties of the federal treatment of gambling winnings and losses.

26 U.S.C. 61(a) puts gambling winnings in gross income (Schedule 1 line 8b).
26 U.S.C. 165(d) lets an itemizer deduct wagering losses up to wagering gains
(Schedule A line 16), and P.L. 119-21 section 70114 allows 90% of the losses
for taxable years beginning after 2025. A dependent's gambling belongs on the
dependent's own return.

YAML cases check single households. These tests check relations between
households, which a YAML case cannot state, at every point of a winnings x
losses x other itemized deductions grid. Each year uses one vectorized
simulation; the grid point with no gambling is the baseline for the others.

- The deduction equals min(share x losses, winnings), with the share restated
  here from the statute (1 through 2025, 0.9 from 2026).
- It is non-negative, never exceeds the winnings or the share of losses, and
  never falls as either rises.
- Adjusted gross income rises by exactly the winnings.
- The deduction is in itemized deductions once, and an itemizer's taxable
  income is AGI less those deductions.
- Income tax never falls as winnings rise and never rises as losses rise.
- Gambling never lowers taxable income or income tax, including when winnings
  equal losses. It raises taxable income by at most the winnings, and by
  exactly the winnings less the deduction for a filer who itemizes either way.
- A dependent's winnings and losses change nothing on the filer's return.

Before PolicyEngine/policyengine-us#9637 was fixed, gross income left the
winnings out while itemizers still deducted the losses, so gambling lowered
tax; the deduction had no 90% share; and it counted a dependent's gambling.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

AMOUNTS = [0, 1, 999, 5_000, 10_000, 25_000, 30_000, 250_000]
# A charitable deduction of 30,000 exceeds every standard deduction, so those
# filers itemize with or without gambling.
OTHER_ITEMIZED = [0, 30_000]
AXES = [AMOUNTS, AMOUNTS, OTHER_ITEMIZED]
GRID = list(itertools.product(*AXES))
SHAPE = tuple(len(axis) for axis in AXES)
WINNINGS, LOSSES, OTHER = (
    np.array([point[i] for point in GRID], dtype=float) for i in range(len(AXES))
)
# Winnings and losses of a dependent child; the first household has none.
DEPENDENT_GAMBLING = [
    (0, 0),
    (10_000, 10_000),
    (30_000, 25_000),
    (250_000, 0),
    (5_000, 250_000),
]
YEARS = [2024, 2025, 2026]
# Share of wagering losses section 165(d) allows (P.L. 119-21 section 70114).
LOSS_SHARE = {2024: 1.0, 2025: 1.0, 2026: 0.9}
WAGES = 60_000
VARIABLES = [
    "adjusted_gross_income",
    "wagering_losses_deduction",
    "itemized_taxable_income_deductions",
    "tax_unit_itemizes",
    "taxable_income",
    "income_tax",
]
# PolicyEngine computes in float32, whose spacing near 300,000 is 3 cents.
ATOL = 0.05


def calculate(year):
    """Grid filers, then parents whose dependent child has the gambling."""
    situation = {"people": {}, "tax_units": {}, "households": {}}

    def add_household(name, members, other_itemized):
        situation["tax_units"][f"t_{name}"] = {
            "members": members,
            "charitable_deduction": {year: float(other_itemized)},
            # No estimated sales tax deduction, so deductions are exact.
            "salt_deduction": {year: 0},
        }
        situation["households"][f"h_{name}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }

    for i, (winnings, losses, other) in enumerate(GRID):
        situation["people"][f"filer_{i}"] = {
            "age": {year: 40},
            "employment_income": {year: WAGES},
            "gambling_winnings": {year: winnings},
            "gambling_losses": {year: losses},
        }
        add_household(f"grid_{i}", [f"filer_{i}"], other)
    for j, (winnings, losses) in enumerate(DEPENDENT_GAMBLING):
        situation["people"][f"parent_{j}"] = {
            "age": {year: 40},
            "employment_income": {year: WAGES},
        }
        situation["people"][f"child_{j}"] = {
            "age": {year: 17},
            "gambling_winnings": {year: winnings},
            "gambling_losses": {year: losses},
        }
        add_household(f"dependent_{j}", [f"parent_{j}", f"child_{j}"], 0)
    simulation = Simulation(situation=situation)
    values = {
        variable: np.asarray(simulation.calculate(variable, year))
        for variable in VARIABLES
    }
    grid = {variable: value[: len(GRID)] for variable, value in values.items()}
    dependents = {variable: value[len(GRID) :] for variable, value in values.items()}
    return grid, dependents


@pytest.fixture(scope="module")
def results():
    return {year: calculate(year) for year in YEARS}


def baseline(values):
    """Each grid point's value with no gambling and the same other deductions."""
    table = values.reshape(SHAPE)
    return np.broadcast_to(table[:1, :1, :], SHAPE).reshape(-1)


@pytest.mark.parametrize("year", YEARS)
def test_deduction_is_the_section_165d_amount(results, year):
    grid, _ = results[year]
    np.testing.assert_allclose(
        grid["wagering_losses_deduction"],
        np.minimum(LOSS_SHARE[year] * LOSSES, WINNINGS),
        atol=ATOL,
    )


@pytest.mark.parametrize("year", YEARS)
def test_deduction_is_bounded_and_monotone(results, year):
    grid, _ = results[year]
    deduction = grid["wagering_losses_deduction"]
    assert np.all(deduction >= 0)
    assert np.all(deduction <= WINNINGS + ATOL)
    assert np.all(deduction <= LOSS_SHARE[year] * LOSSES + ATOL)
    table = deduction.reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) >= -ATOL), "falls as winnings rise"
    assert np.all(np.diff(table, axis=1) >= -ATOL), "falls as losses rise"


@pytest.mark.parametrize("year", YEARS)
def test_winnings_are_in_adjusted_gross_income(results, year):
    grid, _ = results[year]
    np.testing.assert_allclose(
        grid["adjusted_gross_income"], WAGES + WINNINGS, atol=ATOL
    )


@pytest.mark.parametrize("year", YEARS)
def test_deduction_is_in_itemized_deductions_once(results, year):
    grid, _ = results[year]
    deduction = grid["wagering_losses_deduction"]
    # No income here reaches the section 68 limitation.
    np.testing.assert_allclose(
        grid["itemized_taxable_income_deductions"], OTHER + deduction, atol=ATOL
    )
    itemizes = grid["tax_unit_itemizes"]
    assert itemizes.any() and not itemizes.all()
    np.testing.assert_allclose(
        grid["taxable_income"][itemizes],
        (WAGES + WINNINGS - OTHER - deduction)[itemizes],
        atol=ATOL,
    )


@pytest.mark.parametrize("year", YEARS)
def test_income_tax_is_monotone_in_winnings_and_losses(results, year):
    grid, _ = results[year]
    table = grid["income_tax"].reshape(SHAPE)
    assert np.all(np.diff(table, axis=0) >= -ATOL), "falls as winnings rise"
    assert np.all(np.diff(table, axis=1) <= ATOL), "rises as losses rise"


@pytest.mark.parametrize("year", YEARS)
def test_gambling_never_lowers_taxable_income_or_income_tax(results, year):
    grid, _ = results[year]
    change = grid["taxable_income"] - baseline(grid["taxable_income"])
    assert np.all(change >= -ATOL), "gambling lowered taxable income"
    assert np.all(change <= WINNINGS + ATOL), "taxed more than the winnings"
    tax_change = grid["income_tax"] - baseline(grid["income_tax"])
    assert np.all(tax_change >= -ATOL), "gambling lowered income tax"
    # Equal winnings and losses are the case the issue reported.
    equal = WINNINGS == LOSSES
    assert np.all(tax_change[equal] >= -ATOL)
    # A filer who itemizes either way pays tax on the winnings less the
    # deduction.
    itemizes_either_way = OTHER > 0
    assert np.all(grid["tax_unit_itemizes"][itemizes_either_way])
    net_gain = WINNINGS - grid["wagering_losses_deduction"]
    np.testing.assert_allclose(
        change[itemizes_either_way], net_gain[itemizes_either_way], atol=ATOL
    )


@pytest.mark.parametrize("year", YEARS)
def test_a_dependents_gambling_does_not_change_the_filers_return(results, year):
    _, dependents = results[year]
    for variable in VARIABLES:
        values = dependents[variable]
        # The first household's child has no gambling.
        np.testing.assert_allclose(
            values.astype(float), float(values[0]), atol=ATOL, err_msg=variable
        )
    assert np.all(dependents["wagering_losses_deduction"] == 0)
    assert np.all(dependents["adjusted_gross_income"] == WAGES)
