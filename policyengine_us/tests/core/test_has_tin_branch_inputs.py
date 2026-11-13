"""``has_tin`` reads its inputs as the simulation asking for it sees them.

A branch stores its inputs under its own name. The formula read the default
branch's, so a ``has_tin`` or ``has_itin`` (the deprecated alias) input set
on a branch, or inherited by a nested branch from its parent, was ignored and
``has_tin`` came from the default branch's inputs instead.

The contract: a canonical ``has_tin`` input wins over a legacy ``has_itin``
input, which wins over the default ``True``. Each is read as the asking
simulation sees it: its own value, then its nearest ancestor's, then the
default branch's. A sibling branch's inputs are invisible.

``calculate`` returns a canonical ``has_tin`` input the simulation can read
without running the formula, so the canonical-input tests call the formula
itself.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period as as_period

from policyengine_us import Simulation
from policyengine_us.variables.household.demographic.person.has_tin import has_tin

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


@pytest.mark.parametrize("nested", [False, True])
def test_formula_reads_branch_or_ancestor_canonical_has_tin(nested):
    simulation = Simulation(situation=_situation())
    simulation.set_input("has_tin", YEAR, np.array([True]))
    simulation.set_input("has_itin", YEAR, np.array([True]))
    branch = simulation.get_branch("without_tin")
    branch.set_input("has_tin", YEAR, np.array([False]))
    target = branch.get_branch("nested") if nested else branch
    sibling = simulation.get_branch("unrelated")

    # The branch's canonical False wins over the legacy True it inherits, and
    # a nested branch inherits it; the simulation and an unrelated sibling
    # keep the default branch's True.
    for current, expected in (
        (target, [False]),
        (simulation, [True]),
        (sibling, [True]),
    ):
        actual = has_tin.formula(current.persons, as_period(YEAR), None)
        assert actual.tolist() == expected


# A simulation tree: the simulation's own (has_tin, has_itin) inputs, then
# each branch as (index of the simulation it branches from, has_tin input,
# has_itin input), where index 0 is the simulation and branch i is index
# i + 1; ``None`` sets no input. Then the order to calculate in.
INPUT = st.sampled_from([None, True, False])


@st.composite
def simulation_trees(draw):
    root = (draw(INPUT), draw(INPUT))
    branches = [
        (draw(st.integers(0, i)), draw(INPUT), draw(INPUT))
        for i in range(draw(st.integers(0, 5)))
    ]
    order = draw(st.permutations(range(len(branches) + 1)))
    return root, branches, order


def _expected_has_tin(chain_inputs) -> bool:
    """The contract, from (has_tin, has_itin) inputs ordered asker first."""
    for position in (0, 1):  # has_tin, then has_itin
        for inputs in chain_inputs:
            if inputs[position] is not None:
                return inputs[position]
    return True


def _set_inputs(simulation, inputs):
    for variable, value in zip(("has_tin", "has_itin"), inputs):
        if value is not None:
            simulation.set_input(variable, YEAR, np.array([value]))


@settings(
    max_examples=12,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(simulation_trees())
# The canonical case above: a branch's has_tin input, a nested branch and an
# unrelated sibling.
@example(
    ((True, True), [(0, False, None), (1, None, None), (0, None, None)], [2, 0, 3, 1])
)
# A branch's legacy input, inherited by a nested branch.
@example(((None, None), [(0, None, False), (1, None, None)], [0, 1, 2]))
# A nearer legacy input loses to an ancestor's canonical one.
@example(((True, None), [(0, None, False), (1, None, None)], [2, 1, 0]))
def test_has_tin_follows_the_branch_read_contract(tree):
    root_inputs, branches, order = tree
    simulation = Simulation(situation=_situation())
    _set_inputs(simulation, root_inputs)
    # Each simulation's inputs are set before anything branches from it, as a
    # formula sets a branch's override right after creating the branch.
    simulations, parents, inputs = [simulation], [None], [root_inputs]
    for i, (parent, *branch_inputs) in enumerate(branches):
        branch = simulations[parent].get_branch(f"branch_{i}")
        _set_inputs(branch, branch_inputs)
        simulations.append(branch)
        parents.append(parent)
        inputs.append(tuple(branch_inputs))

    def expected(index):
        chain = []
        while index is not None:
            chain.append(inputs[index])
            index = parents[index]
        return _expected_has_tin(chain)

    for index in order:
        formula = has_tin.formula(simulations[index].persons, as_period(YEAR), None)
        assert formula.tolist() == [expected(index)], ("formula", index)
    for index in order:
        calculated = simulations[index].calculate("has_tin", YEAR)
        assert calculated.tolist() == [expected(index)], ("calculate", index)
