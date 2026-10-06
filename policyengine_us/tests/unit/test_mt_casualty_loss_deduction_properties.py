"""Properties of the Montana casualty and theft loss deduction (2021-2023).

The 2021-2023 Form 2 instructions (Itemized Deductions Schedule, line 15) say
to complete federal Form 4684 with Montana AGI in place of federal AGI, and
that spouses filing separately each complete their own Form 4684. Each test
evaluates every point of an input grid in one vectorized simulation, so the
properties hold for all grid inputs rather than for a few examples:

- both variants match a closed-form reference of Form 4684 lines 11-12 and
  17-18: the loss less $100, above 10% of Montana AGI;
- a joint return counts the spouses' losses once, however many members the
  tax unit has, and Montana's joint itemized deductions add it once;
- filing separately, each spouse deducts only their own loss, floored at their
  own Montana AGI;
- a dependent's loss is left to the dependent's own return on both paths;
- the deductions are non-negative, never exceed the loss less $100, rise with
  the loss and fall with Montana AGI;
- for a single filer the joint and separate variants agree;
- the deduction ends in 2024, when Montana discontinued its Itemized
  Deductions Schedule.

The model has no input that distinguishes federally declared disaster losses,
so, like the federal deduction, it allows no personal casualty loss from 2018
unless gov.irs.deductions.itemized.casualty.active is on; a reform switches it
on so the properties are not vacuous.
"""

import itertools

import numpy as np
import pytest
from policyengine_core.reforms import Reform

from policyengine_us import Simulation

REDUCTION = 100  # Form 4684 line 11
FLOOR = 0.1  # Form 4684 line 17

HEAD_LOSSES = [0, 80, 100, 101, 5_000, 30_000]
SPOUSE_LOSSES = [0, 100, 5_000]
HEAD_AGIS = [0, 40_000, 300_000]
SPOUSE_AGIS = [0, 60_000]
# (number of dependents, the first dependent's loss)
DEPENDENTS = [(0, 0), (1, 0), (1, 2_000), (2, 0)]
COUPLE_GRID = list(
    itertools.product(HEAD_LOSSES, SPOUSE_LOSSES, HEAD_AGIS, SPOUSE_AGIS, DEPENDENTS)
)
SINGLE_GRID = list(itertools.product(HEAD_LOSSES, HEAD_AGIS))
YEARS = [2021, 2022, 2023, 2024]

ACTIVE = Reform.from_dict(
    {"gov.irs.deductions.itemized.casualty.active": {"2010-01-01.2100-12-31": True}},
    country_id="us",
)


def reference(loss, agi):
    return np.maximum(np.maximum(loss - REDUCTION, 0) - FLOOR * agi, 0)


def every_year(value):
    return {year: value for year in YEARS}


@pytest.fixture(scope="module")
def grid():
    """One simulation holding every couple and single-filer grid point."""
    people, tax_units, households = {}, {}, {}
    roles = []  # (unit index, role) for each person, in order
    for i, (l1, l2, a1, a2, (n_deps, dep_loss)) in enumerate(COUPLE_GRID):
        members = [f"c{i}_head", f"c{i}_spouse"]
        people[members[0]] = {
            "age": every_year(40),
            "casualty_loss": every_year(l1),
            "mt_agi_indiv": every_year(a1),
        }
        people[members[1]] = {
            "age": every_year(40),
            "casualty_loss": every_year(l2),
            "mt_agi_indiv": every_year(a2),
        }
        roles += [(i, "head"), (i, "spouse")]
        for d in range(n_deps):
            name = f"c{i}_dep{d}"
            people[name] = {
                "age": every_year(10),
                "is_tax_unit_dependent": every_year(True),
                "casualty_loss": every_year(dep_loss if d == 0 else 0),
                "mt_agi_indiv": every_year(0),
            }
            members.append(name)
            roles.append((i, "dependent"))
        tax_units[f"c{i}"] = {"members": members, "mt_agi_joint": every_year(a1 + a2)}
        households[f"c{i}"] = {"members": members, "state_code": every_year("MT")}
    for j, (loss, agi) in enumerate(SINGLE_GRID):
        name = f"s{j}"
        people[name] = {
            "age": every_year(40),
            "casualty_loss": every_year(loss),
            "mt_agi_indiv": every_year(agi),
        }
        roles.append((len(COUPLE_GRID) + j, "single"))
        tax_units[name] = {"members": [name], "mt_agi_joint": every_year(agi)}
        households[name] = {"members": [name], "state_code": every_year("MT")}
    # Zero the other itemized deductions so the aggregators show the casualty
    # loss alone; the grid has no medical, care, charitable or interest items.
    for person in people.values():
        person["mt_salt_deduction"] = every_year(0)
        person["mt_federal_income_tax_deduction_indiv"] = every_year(0)
    for unit in tax_units.values():
        unit["mt_federal_income_tax_deduction_unit"] = every_year(0)
    sim = Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households},
        reform=ACTIVE,
    )
    unit = np.array([r[0] for r in roles])
    role = np.array([r[1] for r in roles])
    return sim, unit, role


def couple_arrays():
    columns = np.array(
        [(l1, l2, a1, a2, n, d) for l1, l2, a1, a2, (n, d) in COUPLE_GRID],
        dtype=float,
    ).T
    return columns  # head loss, spouse loss, head AGI, spouse AGI, deps, dep loss


@pytest.mark.parametrize("year", [2021, 2022, 2023])
def test_joint_return_counts_the_unit_loss_once(grid, year):
    sim, unit, role = grid
    l1, l2, a1, a2, _, _ = couple_arrays()
    n = len(COUPLE_GRID)
    joint = sim.calculate("mt_casualty_loss_deduction_joint", year)[:n]
    # A dependent's loss is left to the dependent's own return.
    np.testing.assert_allclose(joint, reference(l1 + l2, a1 + a2))
    # Montana's joint itemized deductions add it once, at the head, however
    # many members the tax unit has.
    itemized = sim.calculate("mt_itemized_deductions_joint", year)
    per_unit = np.bincount(unit, weights=itemized)[:n]
    np.testing.assert_allclose(per_unit, joint)
    assert np.all(itemized[(role != "head") & (role != "single")] == 0)
    assert np.all(joint >= 0)
    assert np.all(joint <= np.maximum(l1 + l2 - REDUCTION, 0))
    # Guard against a vacuous pass.
    assert joint.max() > 0


@pytest.mark.parametrize("year", [2021, 2022, 2023])
def test_separate_filers_deduct_only_their_own_loss(grid, year):
    sim, unit, role = grid
    l1, l2, a1, a2, _, _ = couple_arrays()
    indiv = sim.calculate("mt_casualty_loss_deduction_indiv", year)
    itemized = sim.calculate("mt_itemized_deductions_indiv", year)
    head = indiv[role == "head"]
    spouse = indiv[role == "spouse"]
    # Each spouse's own Form 4684, on their own Montana AGI; a dependent's
    # loss is in neither column.
    np.testing.assert_allclose(head, reference(l1, a1))
    np.testing.assert_allclose(spouse, reference(l2, a2))
    assert np.all(indiv[role == "dependent"] == 0)
    # A spouse without a loss deducts nothing, whatever the other spouse lost.
    assert np.all(spouse[l2 == 0] == 0)
    assert np.all(head[l1 == 0] == 0)
    # The separate itemized deductions carry each spouse's own amount.
    np.testing.assert_allclose(itemized[role == "head"], head)
    np.testing.assert_allclose(itemized[role == "spouse"], spouse)
    assert np.all(itemized[role == "dependent"] == 0)
    assert np.all(indiv >= 0)
    assert head.max() > 0 and spouse.max() > 0


@pytest.mark.parametrize("year", [2021, 2022, 2023])
def test_single_filer_variants_agree_and_are_monotone(grid, year):
    sim, unit, role = grid
    single = role == "single"
    single_units = unit[single]
    loss = np.array([g[0] for g in SINGLE_GRID], dtype=float)
    agi = np.array([g[1] for g in SINGLE_GRID], dtype=float)
    indiv = sim.calculate("mt_casualty_loss_deduction_indiv", year)[single]
    joint = sim.calculate("mt_casualty_loss_deduction_joint", year)[single_units]
    np.testing.assert_allclose(joint, reference(loss, agi))
    np.testing.assert_allclose(indiv, joint)
    table = joint.reshape(len(HEAD_LOSSES), len(HEAD_AGIS))
    assert np.all(np.diff(table, axis=0) >= 0), "falls as the loss rises"
    assert np.all(np.diff(table, axis=1) <= 0), "rises as Montana AGI rises"


def test_deduction_ends_with_the_2024_schedule(grid):
    sim, _, _ = grid
    assert np.all(sim.calculate("mt_casualty_loss_deduction_joint", 2024) == 0)
    assert np.all(sim.calculate("mt_casualty_loss_deduction_indiv", 2024) == 0)
    # The same inputs are deductible in 2023.
    assert sim.calculate("mt_casualty_loss_deduction_joint", 2023).max() > 0
