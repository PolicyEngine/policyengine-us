"""Branches that calculate one period under overridden inputs.

A policyengine-core branch starts as a copy of every array its parent has
cached, and ``set_input`` on the branch stores the new value without clearing
anything that was calculated from the old one. A branch therefore answers any
variable its parent has already calculated with the parent's value, whatever
the branch's inputs say.

``get_override_branch`` makes the override reach every value the branch
calculates:

- A branch serves one period. Asked for another period, it is created again
  from the parent as the parent stands then, as a simulation calculating only
  that period would create it.
- When the branch is created, it keeps the parent's cache only if the parent
  has no value yet for any overridden variable and period. A cached value
  cannot have been calculated from a value that did not exist, so the
  parent's cache is then safe to share; this is the usual case, where a
  formula branches while its parent is still calculating the variable the
  branch overrides. Otherwise the branch drops every array it copied except
  inputs, and calculates the rest itself.
- A branch reused within its period with different inputs is created again.
"""

from typing import Dict, Tuple, Union

import numpy as np
from policyengine_core.periods import Period
from policyengine_core.periods import period as to_period
from policyengine_core.simulations import Simulation

Override = Union[np.ndarray, Tuple[Period, np.ndarray]]


def _overrides(period: Period, inputs: Dict[str, Override]):
    for variable, value in inputs.items():
        if isinstance(value, tuple):
            input_period, value = value
            yield variable, to_period(input_period), np.asarray(value)
        else:
            yield variable, period, np.asarray(value)


def _is_known(simulation: Simulation, variable: str, period: Period) -> bool:
    holder = simulation.get_holder(variable)
    if holder.variable.is_neutralized:
        return False
    return holder.get_array(period, simulation.branch_name) is not None


def drop_inherited_values(branch: Simulation) -> None:
    """Delete every array ``branch`` holds except inputs.

    Inputs are the variables the simulation was built with and each value set
    through ``set_input`` on a branch this one reads.
    """
    input_variables = set(branch.input_variables)
    user_input_keys = getattr(branch, "_user_input_keys", set())
    visible_branches = set(branch._get_visible_branch_names())
    for population in branch.populations.values():
        for name, holder in population._holders.items():
            if name in input_variables:
                continue
            for branch_name, known_period in holder.get_known_branch_periods():
                if (
                    branch_name in visible_branches
                    and (name, branch_name, known_period) in user_input_keys
                ):
                    continue
                # Exact key: ``Holder.delete_arrays`` would also delete any
                # input stored at a sub-period of ``known_period``.
                key = f"{branch_name}:{known_period}"
                holder._memory_storage._arrays.pop(key, None)
                if holder._disk_storage is not None:
                    holder._disk_storage._files.pop(
                        f"{branch_name}_{known_period}", None
                    )
    branch._fast_cache = {}


def get_override_branch(
    simulation: Simulation,
    name: str,
    period: Period,
    inputs: Dict[str, Override],
) -> Simulation:
    """Return ``simulation``'s branch ``name`` for ``period``, with ``inputs`` set.

    ``inputs`` maps each overridden variable to its value for ``period``, or
    to a ``(period, value)`` pair for another period (e.g. a month).
    """
    overrides = list(_overrides(period, inputs))
    if name == simulation.branch_name:
        # Already inside this branch (core's get_branch returns the
        # simulation itself): only the inputs need setting.
        for variable, input_period, value in overrides:
            simulation.set_input(variable, input_period, value)
        return simulation
    branch = simulation.branches.get(name)
    if branch is not None and (
        getattr(branch, "branch_period", None) != period
        or not _same_overrides(branch, overrides)
    ):
        del simulation.branches[name]
        branch = None
    if branch is None:
        parent_knows_override = any(
            _is_known(simulation, variable, input_period)
            for variable, input_period, _ in overrides
        )
        branch = simulation.get_branch(name)
        branch.branch_period = period
        if parent_knows_override:
            drop_inherited_values(branch)
        for variable, input_period, value in overrides:
            branch.set_input(variable, input_period, value)
        branch.branch_overrides = overrides
    return branch


def _same_overrides(branch: Simulation, overrides) -> bool:
    previous = getattr(branch, "branch_overrides", None)
    if previous is None or len(previous) != len(overrides):
        return False
    return all(
        variable == previous_variable
        and input_period == previous_period
        and np.array_equal(value, previous_value)
        for (variable, input_period, value), (
            previous_variable,
            previous_period,
            previous_value,
        ) in zip(overrides, previous)
    )


def get_branch_for_period(
    simulation: Simulation, name: str, period: Period
) -> Simulation:
    """Return ``simulation``'s branch ``name`` for ``period``, created per period.

    For branches that change the tax-benefit system rather than inputs: the
    caller swaps the system and deletes the variables it recalculates.
    """
    if name == simulation.branch_name:
        return simulation
    branch = simulation.branches.get(name)
    if branch is not None and getattr(branch, "branch_period", None) != period:
        del simulation.branches[name]
    branch = simulation.get_branch(name)
    branch.branch_period = period
    return branch
