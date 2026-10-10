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
- A caller can ask the branch never to keep the parent's calculated values
  (``inherit_calculated=False``). The parent can hold a value that depends on
  the overridden variable although it has no value for that variable yet:
  one it calculated in another branch, which chose the overridden variable
  for itself. The branches that fix the claim of right method (26 U.S.C.
  1341) start from inputs for that reason.

``get_branch_for_period`` is the same with no inputs, for branches that
change the tax-benefit system rather than inputs: the caller swaps the system
and deletes the variables it recalculates.
"""

from typing import Dict, Set, Tuple, Union

import numpy as np
from policyengine_core.periods import ETERNITY, Period
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


def _input_keys(branch: Simulation) -> Set[Tuple[str, str, Period]]:
    """The (variable, branch name, period) keys ``branch`` reads as inputs.

    policyengine-core records each key that ``set_input`` stores, whether
    from the dataset, the situation or a branch, in one set shared by a
    simulation and all its branches. ``branch`` reads its own keys and its
    ancestors'.
    """
    visible_branches = set(branch._get_visible_branch_names())
    return {
        key
        for key in getattr(branch, "_user_input_keys", set())
        if key[1] in visible_branches
    }


def drop_inherited_values(branch: Simulation) -> None:
    """Delete every array ``branch`` holds except inputs.

    An array is kept only if ``set_input`` stored it, on this branch or one it
    reads, for that variable and period. A value calculated for one period is
    dropped even when the same variable is an input for another period.
    """
    input_keys = _input_keys(branch)
    # An eternal variable stores every period under one key, while the input
    # key records the period it was set for, so match it by branch only.
    eternal_inputs = {(name, branch_name) for name, branch_name, _ in input_keys}
    for population in branch.populations.values():
        for name, holder in population._holders.items():
            eternal = holder.variable.definition_period == ETERNITY
            for branch_name, known_period in holder.get_known_branch_periods():
                if (
                    (name, branch_name) in eternal_inputs
                    if eternal
                    else (name, branch_name, known_period) in input_keys
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
    inherit_calculated: bool = True,
) -> Simulation:
    """Return ``simulation``'s branch ``name`` for ``period``, with ``inputs`` set.

    ``inputs`` maps each overridden variable to its value for ``period``, or
    to a ``(period, value)`` pair for another period (e.g. a month). With
    ``inherit_calculated=False`` a new branch keeps only inputs, whether or
    not the parent has calculated an overridden variable.
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
        if parent_knows_override or not inherit_calculated:
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
