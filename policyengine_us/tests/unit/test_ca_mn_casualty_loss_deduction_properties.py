"""Properties of California's and Minnesota's casualty loss deductions.

Both states allow a personal casualty or theft loss under 26 U.S.C. 165(h)
without the federal limit to declared disasters (Cal. Rev. & Tax. Code
17204(b), Schedule CA (540) line 15; Minn. Stat. 290.0122, subd. 8, Schedule
M1CAT). Each reduces the loss by $100 (Form 4684 line 11; M1CAT line 11) and
allows the rest above 10% of federal adjusted gross income (Form 4684 line 17
and FTB Publication 1034; M1CAT lines 18-19). A joint return is one individual
for the $100 rule, and a dependent's loss belongs on the dependent's own
return. The model records one loss amount per person and no event count, so a
return's losses are treated as one casualty.

`ca_casualty_loss_deduction` and `mn_casualty_loss_deduction` are two copies
of that computation. Hypothesis draws batches of tax units (single or joint,
with up to two dependents who have their own losses), places each in
California and in Minnesota, and runs each batch as one vectorized baseline
simulation. For every tax unit and year:

1. Each copy equals a closed-form reference on the head's and spouse's losses:
   max(max(loss - 100, 0) - 10% x max(AGI, 0), 0). Dependents' losses never
   enter it, and neither does California AGI.
2. Bounds: 0 <= deduction <= max(loss - 100, 0).
3. Each copy is zero outside its state.
4. Differential: the two copies agree on the same drawn units.
5. The federal `casualty_loss_deduction` is zero in these years, so neither
   state follows the federal suspension.

A deterministic grid adds the boundary inputs ($0, $99, $100, $101, the floor
plus $100) and checks monotonicity: each copy rises with the loss and falls
with AGI, and is zero for a loss of $100 or less.
"""

import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

REDUCTION = 100  # Form 4684 line 11; Schedule M1CAT line 11
FLOOR = 0.1  # Form 4684 line 17; Schedule M1CAT line 19
TOLERANCE = 0.01
CA_AGI_OFFSET = 7_000  # makes California AGI differ from federal AGI
# 2018 is the first year of the federal suspension; 2026 follows California's
# move to a January 1, 2025 conformity date.
YEARS = [2018, 2026]
STATE_OF = {
    "ca_casualty_loss_deduction": "CA",
    "mn_casualty_loss_deduction": "MN",
}
STATES = list(STATE_OF.values())


def reference(loss, agi):
    reduced = np.maximum(loss - REDUCTION, 0)
    return np.maximum(reduced - FLOOR * np.maximum(agi, 0), 0)


def every_year(value):
    return {year: value for year in YEARS}


def build_situation(units):
    """Place each unit in each state, with the same federal AGI."""
    people, tax_units, households = {}, {}, {}
    rows = []  # (filer loss, AGI, state) for each tax unit, in order
    for state in STATES:
        for i, unit in enumerate(units):
            name = f"{state}{i}"
            members = [f"{name}_head"]
            people[members[0]] = {
                "age": every_year(40),
                "casualty_loss": every_year(unit["head_loss"]),
            }
            filer_loss = unit["head_loss"]
            if unit["joint"]:
                members.append(f"{name}_spouse")
                people[members[-1]] = {
                    "age": every_year(40),
                    "casualty_loss": every_year(unit["spouse_loss"]),
                }
                filer_loss += unit["spouse_loss"]
            for d, dependent_loss in enumerate(unit["dependent_losses"]):
                members.append(f"{name}_dep{d}")
                people[members[-1]] = {
                    "age": every_year(10),
                    "is_tax_unit_dependent": every_year(True),
                    "casualty_loss": every_year(dependent_loss),
                }
            agi = unit["agi"]
            tax_units[name] = {
                "members": members,
                "adjusted_gross_income": every_year(agi),
                # California's floor is on federal AGI (FTB Publication 1034),
                # so a different California AGI must not move its copy.
                "ca_agi": every_year(agi + CA_AGI_OFFSET),
            }
            households[name] = {"members": members, "state_code": every_year(state)}
            rows.append((filer_loss, agi, state))
    situation = {"people": people, "tax_units": tax_units, "households": households}
    loss, agi, state = (np.array(column) for column in zip(*rows))
    return situation, loss.astype(float), agi.astype(float), state


def check_reference_and_bounds(sim, loss, agi, state):
    for variable, own_state in STATE_OF.items():
        for year in YEARS:
            value = sim.calculate(variable, year)
            expected = np.where(state == own_state, reference(loss, agi), 0)
            np.testing.assert_allclose(
                value, expected, atol=TOLERANCE, err_msg=f"{variable} {year}"
            )
            assert np.all(value >= 0)
            assert np.all(value <= np.maximum(loss - REDUCTION, 0) + TOLERANCE)


def check_copies_agree(sim, state):
    for year in YEARS:
        california = sim.calculate("ca_casualty_loss_deduction", year)
        minnesota = sim.calculate("mn_casualty_loss_deduction", year)
        # The same drawn units, in the same order, sit in each state.
        np.testing.assert_allclose(
            california[state == "CA"], minnesota[state == "MN"], atol=TOLERANCE
        )
        # Neither state follows the federal suspension.
        assert np.all(sim.calculate("casualty_loss_deduction", year) == 0)


money = st.one_of(
    st.sampled_from([0, 50, 99, 100, 101, 150]),
    st.integers(0, 60_000),
).map(float)
agis = st.one_of(
    st.sampled_from([0, 1_000, 50_000]),
    st.integers(-20_000, 300_000),
).map(float)
tax_unit_strategy = st.fixed_dictionaries(
    {
        "joint": st.booleans(),
        "head_loss": money,
        "spouse_loss": money,
        "dependent_losses": st.lists(money, max_size=2),
        "agi": agis,
    }
)
SETTINGS = dict(
    max_examples=20,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(tax_unit_strategy, min_size=4, max_size=15))
def test_copies_match_the_form_4684_reference(units):
    situation, loss, agi, state = build_situation(units)
    sim = Simulation(situation=situation)
    check_reference_and_bounds(sim, loss, agi, state)
    check_copies_agree(sim, state)


GRID_LOSSES = [0, 50, 99, 100, 101, 150, 5_000, 10_100, 10_101, 30_000]
GRID_AGIS = [-10_000, 0, 1_000, 50_000, 100_000, 300_000]
GRID_DEPENDENT_LOSSES = [0, 20_000]


def grid_situation():
    units = [
        {
            "joint": False,
            "head_loss": float(loss),
            "spouse_loss": 0.0,
            "dependent_losses": [float(dependent_loss)],
            "agi": float(agi),
        }
        for loss, agi, dependent_loss in itertools.product(
            GRID_LOSSES, GRID_AGIS, GRID_DEPENDENT_LOSSES
        )
    ]
    return build_situation(units)


@pytest.fixture(scope="module")
def grid():
    situation, loss, agi, state = grid_situation()
    return Simulation(situation=situation), loss, agi, state


@pytest.mark.parametrize("variable, year", list(itertools.product(STATE_OF, YEARS)))
def test_grid_monotone_and_boundaries(grid, variable, year):
    sim, loss, agi, state = grid
    rows = state == STATE_OF[variable]
    value = sim.calculate(variable, year)[rows]
    np.testing.assert_allclose(value, reference(loss[rows], agi[rows]), atol=TOLERANCE)
    shape = (len(GRID_LOSSES), len(GRID_AGIS), len(GRID_DEPENDENT_LOSSES))
    table = value.reshape(shape)
    # A dependent's loss never changes the filer's deduction.
    np.testing.assert_allclose(table[..., 0], table[..., 1], atol=TOLERANCE)
    assert np.all(np.diff(table, axis=0) >= -TOLERANCE), "falls as the loss rises"
    assert np.all(np.diff(table, axis=1) <= TOLERANCE), "rises as AGI rises"
    # A loss of $100 or less is absorbed by the $100 reduction.
    small = np.array(GRID_LOSSES) <= REDUCTION
    assert np.all(table[small] == 0)
    # Guard against a vacuous pass.
    assert table.max() > 0
