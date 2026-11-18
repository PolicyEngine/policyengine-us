"""Properties of the Puerto Rico casualty loss deductions.

Each test evaluates every point of an input grid in one vectorized
simulation, so the properties hold for all grid inputs rather than for a few
examples:

- the deductions match a closed-form reference of P.R. Internal Revenue Code
  of 2011 Section 1033.15(a)(10): (A) the principal residence loss in full,
  or half for a spouse filing separately, with no cap; (B) the automobile and
  household goods loss plus any carryover, capped at $5,000, or half of the
  loss capped at $2,500 for a spouse filing separately;
- they are non-negative and stay within the loss and the cap, and (B) rises
  with the loss and the carryover;
- the generic casualty_loss input, which holds any casualty or theft loss,
  changes neither deduction;
- both deductions flow into pr_deductions.
"""

import itertools

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2025
RESIDENCE_LOSSES = [0, 1, 2_500, 20_000]
PERSONAL_LOSSES = [0, 1, 2_500, 4_999, 5_000, 5_001, 10_000]
CARRYOVERS = [0, 1_000, 6_000]
FILING_STATUSES = [
    "SINGLE",
    "JOINT",
    "SEPARATE",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
]
GENERIC_LOSSES = [0, 50_000]
GRID = list(
    itertools.product(
        RESIDENCE_LOSSES,
        PERSONAL_LOSSES,
        CARRYOVERS,
        FILING_STATUSES,
        GENERIC_LOSSES,
    )
)

SEPARATE_SHARE = 0.5
CAP = 5_000
SEPARATE_CAP = 2_500


def grid_simulation():
    """One single-person tax unit per grid point, all in Puerto Rico."""
    situation = {"people": {}, "tax_units": {}, "households": {}}
    for i, (residence, personal, carryover, status, generic) in enumerate(GRID):
        person = f"p{i}"
        situation["people"][person] = {
            "age": {YEAR: 40},
            "pr_principal_residence_casualty_loss": {YEAR: residence},
            "pr_personal_property_casualty_loss": {YEAR: personal},
            "casualty_loss": {YEAR: generic},
        }
        situation["tax_units"][f"t{i}"] = {
            "members": [person],
            "filing_status": {YEAR: status},
            "pr_personal_property_casualty_loss_carryover": {YEAR: carryover},
        }
        situation["households"][f"h{i}"] = {
            "members": [person],
            "state_code": {YEAR: "PR"},
        }
    return Simulation(situation=situation)


@pytest.fixture(scope="module")
def out():
    """The grid's results, computed once and only read by the tests."""
    sim = grid_simulation()
    return {
        variable: sim.calculate(variable, YEAR)
        for variable in (
            "pr_casualty_loss_deduction",
            "pr_personal_property_casualty_loss_deduction",
            "pr_deductions",
        )
    }


def column(index):
    values = [g[index] for g in GRID]
    if isinstance(values[0], str):
        return np.array(values)
    return np.array(values, dtype=float)


def test_deductions_match_the_statute(out):
    residence, personal, carryover, status = (column(i) for i in range(4))
    separate = status == "SEPARATE"
    share = np.where(separate, SEPARATE_SHARE, 1)
    cap = np.where(separate, SEPARATE_CAP, CAP)
    np.testing.assert_allclose(out["pr_casualty_loss_deduction"], share * residence)
    np.testing.assert_allclose(
        out["pr_personal_property_casualty_loss_deduction"],
        np.minimum(share * personal + carryover, cap),
    )


def test_deductions_are_bounded(out):
    residence, status = column(0), column(3)
    cap = np.where(status == "SEPARATE", SEPARATE_CAP, CAP)
    line_2 = out["pr_casualty_loss_deduction"]
    line_5 = out["pr_personal_property_casualty_loss_deduction"]
    assert np.all(line_2 >= 0) and np.all(line_2 <= residence)
    assert np.all(line_5 >= 0) and np.all(line_5 <= cap)
    # Guard against a vacuous pass: the cap binds somewhere.
    assert np.any(line_5 == cap) and np.any(line_5 < cap)


def test_personal_property_deduction_rises_with_loss_and_carryover(out):
    line_5 = out["pr_personal_property_casualty_loss_deduction"]
    table = line_5.reshape(
        len(RESIDENCE_LOSSES),
        len(PERSONAL_LOSSES),
        len(CARRYOVERS),
        len(FILING_STATUSES),
        len(GENERIC_LOSSES),
    )
    assert np.all(np.diff(table, axis=1) >= 0), "falls as the loss rises"
    assert np.all(np.diff(table, axis=2) >= 0), "falls as the carryover rises"


def test_generic_casualty_loss_has_no_effect(out):
    for variable, values in out.items():
        table = values.reshape(-1, len(GENERIC_LOSSES))
        np.testing.assert_allclose(table[:, 1], table[:, 0], err_msg=variable)


def test_both_deductions_flow_into_the_total(out):
    np.testing.assert_allclose(
        out["pr_deductions"],
        out["pr_casualty_loss_deduction"]
        + out["pr_personal_property_casualty_loss_deduction"],
    )
