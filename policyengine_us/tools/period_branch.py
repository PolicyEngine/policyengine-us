"""Formula branches that calculate one period, under overridden inputs.

A Core branch snapshots its parent's inputs and results. Core's ``set_input``
invalidates calculated results in that branch while preserving its supplied
inputs, so this module does not inspect or clear Core storage. It controls the
lifetime of formula-specific branches:

- A branch serves one period. Asked for another period, it is created again
  from the parent as the parent stands then, as a simulation calculating only
  that period would create it.
- A branch reused within its period with different inputs is created again.
- A formula branch is created again if its parent's supplied-input revision
  changes. Existing named branch snapshots are otherwise left untouched.

``get_branch_for_period`` is the same with no inputs, for branches that
change the tax-benefit system rather than inputs: the caller swaps the system
and deletes the variables it recalculates.
"""

from typing import Dict, Tuple, Union

import numpy as np
from policyengine_core.data_storage import CachedArrayEntry
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
        or getattr(branch, "branch_parent_input_revision", None)
        != simulation.input_revision
        or not _same_overrides(branch, overrides)
    ):
        del simulation.branches[name]
        branch = None
    if branch is None:
        branch = simulation.get_branch(name)
        branch.branch_period = period
        branch.branch_parent_input_revision = simulation.input_revision
        for variable, input_period, value in overrides:
            branch.set_input(variable, input_period, value)
        branch.branch_overrides = tuple(
            (variable, input_period, CachedArrayEntry.from_value(value).read())
            for variable, input_period, value in overrides
        )
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
