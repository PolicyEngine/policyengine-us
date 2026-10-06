"""Properties of PolicyEngine's copies of the Form 4684 casualty loss computation.

26 U.S.C. 165(h)(1) reduces each personal casualty loss by $100 (Form 4684
line 11), and 165(h)(2)(A) allows the rest only above 10% of adjusted gross
income (line 17). A joint return is one individual for the $100 rule
(165(h)(4)(B)), and a dependent's loss belongs on the dependent's own return.
The model records one loss amount per person and no event count, so a return's
losses are treated as one casualty. Four variables copy the computation:

- the federal `casualty_loss_deduction`, on federal AGI, suspended from 2018
  (gov.irs.deductions.itemized.casualty.active);
- New York's `ny_casualty_loss_deduction`, on federal AGI, under the 2017
  federal rules in every year (Form IT-196 line 20);
- Alabama's `al_casualty_loss_deduction`, on Alabama AGI, following 165(h) as in
  effect from time to time, so suspended with the federal deduction;
- Hawaii's `hi_casualty_loss_deduction`, on Hawaii AGI (floored at zero), with
  Hawaii's own $100, allowed for non-disaster losses through 2025 (Act 35,
  SLH 2026, adopts 165(h)(5) from 2026).

Hypothesis draws batches of tax units (single or joint, with up to two
dependents who have their own losses), each placed in New York, Alabama and
Hawaii, and gives every copy the same AGI. Each batch runs as one vectorized
baseline simulation. For every tax unit and year:

1. Each copy equals a closed-form reference on the head's and spouse's losses:
   gate x max(max(loss - 100, 0) - 10% x max(AGI, 0), 0). Dependents' losses
   never enter it.
2. Bounds: 0 <= deduction <= max(loss - 100, 0).
3. A state copy is zero outside its state.
4. Differential: where their gates are on, the four copies agree with each
   other, since they share the computation and the AGI.

A deterministic grid adds the boundary inputs ($0, $99, $100, $101, the floor
plus $100) and checks monotonicity: each copy rises with the loss and falls
with AGI, and is zero for a loss of $100 or less. The YAML tests cover a reform
that lifts the federal suspension, which Alabama follows and Hawaii does not.
"""

import itertools

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

REDUCTION = 100  # Form 4684 line 11; HRS 235-2.4(l)(1)
FLOOR = 0.1  # Form 4684 line 17
TOLERANCE = 0.01
STATES = ["NY", "AL", "HI"]
YEARS = [2017, 2025, 2026]
# Whether each copy allows a non-disaster loss, by year, in baseline. Hawaii's
# variables start in 2018, when its itemized deductions do.
GATES = {
    "casualty_loss_deduction": {2017: 1, 2025: 0, 2026: 0},
    "ny_casualty_loss_deduction": {2017: 1, 2025: 1, 2026: 1},
    "al_casualty_loss_deduction": {2017: 1, 2025: 0, 2026: 0},
    "hi_casualty_loss_deduction": {2025: 1, 2026: 0},
}
STATE_OF = {
    "ny_casualty_loss_deduction": "NY",
    "al_casualty_loss_deduction": "AL",
    "hi_casualty_loss_deduction": "HI",
}


def reference(loss, agi):
    reduced = np.maximum(loss - REDUCTION, 0)
    return np.maximum(reduced - FLOOR * np.maximum(agi, 0), 0)


def every_year(value):
    return {year: value for year in YEARS}


def build_situation(units):
    """Place each unit in each state, with the same AGI for every copy."""
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
                "al_agi": every_year(agi),
                "hi_agi": every_year(agi),
            }
            households[name] = {"members": members, "state_code": every_year(state)}
            rows.append((filer_loss, agi, state))
    situation = {"people": people, "tax_units": tax_units, "households": households}
    loss, agi, state = (np.array(column) for column in zip(*rows))
    return situation, loss.astype(float), agi.astype(float), state


def check_reference_and_bounds(sim, loss, agi, state, gates):
    for variable, by_year in gates.items():
        for year, gate in by_year.items():
            value = sim.calculate(variable, year)
            expected = gate * reference(loss, agi)
            in_state = state == STATE_OF.get(variable, state)
            expected = np.where(in_state, expected, 0)
            np.testing.assert_allclose(
                value, expected, atol=TOLERANCE, err_msg=f"{variable} {year}"
            )
            assert np.all(value >= 0)
            assert np.all(value <= np.maximum(loss - REDUCTION, 0) + TOLERANCE)


def check_copies_agree(sim, state, gates):
    for year in YEARS:
        on = [v for v, by_year in gates.items() if by_year.get(year) == 1]
        federal = sim.calculate("casualty_loss_deduction", year)
        for variable in on:
            value = sim.calculate(variable, year)
            if variable in STATE_OF:
                in_state = state == STATE_OF[variable]
                if "casualty_loss_deduction" in on:
                    np.testing.assert_allclose(
                        value[in_state], federal[in_state], atol=TOLERANCE
                    )
                for other in on:
                    if other in STATE_OF and other != variable:
                        # Compare the same drawn units across states.
                        other_state = state == STATE_OF[other]
                        np.testing.assert_allclose(
                            value[in_state],
                            sim.calculate(other, year)[other_state],
                            atol=TOLERANCE,
                        )


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
    check_reference_and_bounds(sim, loss, agi, state, GATES)
    check_copies_agree(sim, state, GATES)


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


@pytest.mark.parametrize(
    "variable, year",
    [(v, y) for v, by_year in GATES.items() for y, gate in by_year.items() if gate],
)
def test_grid_monotone_and_boundaries(grid, variable, year):
    sim, loss, agi, state = grid
    rows = state == STATE_OF.get(variable, "NY")
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
