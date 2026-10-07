"""Formula branches that calculate one period, under overridden inputs.

A policyengine-core branch starts from every array its parent has cached when
the branch is created and never sees the parent's later calculations, and
``set_input`` on the branch stores the new value without clearing anything
that was calculated from the old one. A branch therefore answers any variable
its parent had already calculated with the parent's value, whatever the
branch's inputs say. A branch kept from another period also answers this
period from a copy taken before any of this period was calculated, unlike the
branch a simulation calculating only this period would create, so a later
year came out differently when an earlier year had been calculated first.

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
  inputs, each for the periods it was set for, and calculates the rest
  itself.
- A branch reused within its period with different inputs is created again.

``get_branch_for_period`` is the same with no inputs, for branches that
change the tax-benefit system rather than inputs: the caller swaps the system
and deletes the variables it recalculates.
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

    An array is kept only if ``set_input`` stored it, on this branch or one it
    reads, for that variable and period. A value calculated for one period is
    dropped even when the same variable is an input for another period.
    """
    branch.clear_calculated_results()


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
    period = to_period(period)
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
    caller swaps the system and deletes the variables it recalculates. Within
    a period the branch is shared; a branch left from another period is
    dropped and created again from the parent as it stands now.
    """
    return get_override_branch(simulation, name, period, {})
