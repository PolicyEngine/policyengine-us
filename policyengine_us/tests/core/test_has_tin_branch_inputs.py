"""``has_tin`` reads its inputs as the simulation asking for it sees them.

A branch stores its inputs under its own name. The formula read the default
branch's, so a ``has_itin`` input (the deprecated alias) set on a branch, or
inherited by a nested branch from its parent, was ignored and ``has_tin``
fell back to ``True``.
"""

import numpy as np

from policyengine_us import Simulation

YEAR = 2026


def _situation() -> dict:
    return {
        "people": {"adult": {"age": {YEAR: 30}}},
        "tax_units": {"tax_unit": {"members": ["adult"]}},
        "households": {"household": {"members": ["adult"], "state_code": {YEAR: "CA"}}},
    }


def test_a_branch_reads_its_own_legacy_has_itin_input():
    simulation = Simulation(situation=_situation())
    branch = simulation.get_branch("without_tin")
    branch.set_input("has_itin", YEAR, np.array([False]))

    assert branch.calculate("has_tin", YEAR).tolist() == [False]
    # The input stays in the branch.
    assert simulation.calculate("has_tin", YEAR).tolist() == [True]


def test_a_nested_branch_reads_its_parents_legacy_has_itin_input():
    simulation = Simulation(situation=_situation())
    branch = simulation.get_branch("without_tin")
    branch.set_input("has_itin", YEAR, np.array([False]))
    nested = branch.get_branch("nested")

    assert nested.calculate("has_tin", YEAR).tolist() == [False]


def test_a_branch_still_reads_the_default_branchs_legacy_input():
    situation = _situation()
    situation["people"]["adult"]["has_itin"] = {YEAR: False}
    simulation = Simulation(situation=situation)
    branch = simulation.get_branch("unchanged")

    assert branch.calculate("has_tin", YEAR).tolist() == [False]
    assert simulation.calculate("has_tin", YEAR).tolist() == [False]
