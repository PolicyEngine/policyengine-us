"""Properties of the Arkansas miscellaneous and casualty loss deductions.

Each test evaluates every point of an input grid in one vectorized
simulation, so the properties hold for all grid inputs rather than for a few
examples:

- the deductions match a closed-form reference of Ark. Code § 26-51-437(a)
  and § 26-51-424(b) (26 U.S.C. § 165(h) as in effect on January 1, 2009);
- they are non-negative, never exceed the expenses or the loss after the
  exclusion, rise with expenses or losses, and fall with Arkansas AGI;
- the joint and separate variants agree on the same inputs;
- they do not depend on the year across the federal TCJA suspension;
- before 2018, the Arkansas miscellaneous deduction equals the federal one
  when Arkansas AGI equals federal AGI, since both apply one 2% floor.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

AMOUNTS = [0, 50, 100, 101, 999, 1_000, 5_000, 5_100, 20_000, 250_000]
AGIS = [0, 1, 10_000, 50_000, 51_000, 100_000, 1_000_000]
GRID = list(itertools.product(AMOUNTS, AGIS))

MISC_FLOOR = 0.02
CASUALTY_FLOOR = 0.1


def casualty_exclusion(year):
    # 26 U.S.C. § 165(h)(1) as in effect on January 1, 2009: "$500 ($100 for
    # taxable years beginning after December 31, 2009)".
    return 500 if year == 2009 else 100


def grid_simulation(year, person_inputs, tax_unit_inputs=None):
    """One single-person tax unit per grid point, all in Arkansas."""
    n = len(GRID)
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i in range(n):
        person = f"p{i}"
        situation["people"][person] = {
            name: {year: values[i].item()} for name, values in person_inputs.items()
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            **{
                name: {year: values[i].item()}
                for name, values in (tax_unit_inputs or {}).items()
            },
        }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {year: "AR"},
        }
    return Simulation(situation=situation)


def grid_arrays():
    amount = np.array([g[0] for g in GRID], dtype=float)
    agi = np.array([g[1] for g in GRID], dtype=float)
    return amount, agi


def misc_reference(expenses, agi):
    return np.maximum(0, expenses - MISC_FLOOR * agi)


def casualty_reference(loss, agi, year):
    after_exclusion = np.maximum(0, loss - casualty_exclusion(year))
    return np.maximum(0, after_exclusion - CASUALTY_FLOOR * agi)


def assert_monotone(values, amount, agi):
    """Non-decreasing in the amount, non-increasing in AGI."""
    table = values.reshape(len(AMOUNTS), len(AGIS))
    assert np.all(np.diff(table, axis=0) >= 0), "falls as the amount rises"
    assert np.all(np.diff(table, axis=1) <= 0), "rises as AGI rises"


YEARS = [2009, 2010, 2015, 2017, 2018, 2022, 2025]


@pytest.mark.parametrize("year", YEARS)
def test_misc_deduction_properties(year):
    expenses, agi = grid_arrays()
    sim = grid_simulation(
        year,
        {"ar_agi_joint": agi, "ar_agi_indiv": agi},
        {"total_misc_deductions": expenses},
    )
    joint = sim.calculate("ar_misc_deduction_joint", year)
    indiv = sim.calculate("ar_misc_deduction_indiv", year)
    np.testing.assert_allclose(joint, misc_reference(expenses, agi))
    np.testing.assert_allclose(indiv, joint)
    assert np.all(joint >= 0)
    assert np.all(joint <= expenses)
    assert_monotone(joint, expenses, agi)


@pytest.mark.parametrize("year", YEARS)
def test_casualty_loss_deduction_properties(year):
    loss, agi = grid_arrays()
    sim = grid_simulation(
        year,
        {"casualty_loss": loss, "ar_agi_joint": agi, "ar_agi_indiv": agi},
    )
    joint = sim.calculate("ar_casualty_loss_deduction_joint", year)
    indiv = sim.calculate("ar_casualty_loss_deduction_indiv", year)
    np.testing.assert_allclose(joint, casualty_reference(loss, agi, year))
    np.testing.assert_allclose(indiv, joint)
    assert np.all(joint >= 0)
    assert np.all(joint <= np.maximum(0, loss - casualty_exclusion(year)))
    assert_monotone(joint, loss, agi)


def test_deductions_do_not_depend_on_the_tcja_suspension():
    amount, agi = grid_arrays()
    results = {}
    for year in range(2010, 2026):
        sim = grid_simulation(
            year,
            {"casualty_loss": amount, "ar_agi_joint": agi},
            {"total_misc_deductions": amount},
        )
        results[year] = (
            sim.calculate("ar_misc_deduction_joint", year),
            sim.calculate("ar_casualty_loss_deduction_joint", year),
        )
    for year, (misc, casualty) in results.items():
        np.testing.assert_allclose(misc, results[2010][0], err_msg=str(year))
        np.testing.assert_allclose(casualty, results[2010][1], err_msg=str(year))
    # Guard against a vacuous pass: the grid has positive deductions.
    assert results[2025][0].max() > 0 and results[2025][1].max() > 0


@pytest.mark.parametrize("year", [2015, 2016, 2017])
def test_misc_deduction_matches_federal_before_2018(year):
    """Differential check against the federal pre-TCJA § 67 deduction."""
    expenses, wages = grid_arrays()
    sim = grid_simulation(
        year,
        {
            "age": np.full(len(GRID), 40),
            "employment_income": wages,
            "unreimbursed_business_employee_expenses": expenses,
        },
    )
    federal_agi = sim.calculate("adjusted_gross_income", year)
    ar_agi = sim.calculate("ar_agi_joint", year)
    # Precondition: with wages only, Arkansas and federal AGI coincide.
    np.testing.assert_allclose(ar_agi, federal_agi)
    np.testing.assert_allclose(
        sim.calculate("ar_misc_deduction_joint", year),
        sim.calculate("misc_deduction", year),
    )
