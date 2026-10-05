from policyengine_core.periods import Period
from policyengine_core.simulations import Simulation


def get_branch_for_period(simulation: Simulation, name: str, period: Period):
    """Return ``simulation``'s branch ``name`` for calculating ``period``.

    A branch copies its parent's cached arrays when it is created and never
    sees the parent's later calculations, and an input set on it does not
    clear values it already copied. What a branch computes for a period
    therefore depends on what its parent had calculated when the branch was
    created. A branch kept from another period answers this period from a copy
    taken before any of this period was calculated, unlike the branch a
    simulation calculating only this period would create, so a later year came
    out differently when an earlier year had been calculated first.

    Within a period the branch is shared as before. A branch left from another
    period is dropped, and the branch is created again from the parent as it
    stands now.
    """
    branch = simulation.branches.get(name)
    if branch is not None and getattr(branch, "branch_period", period) != period:
        del simulation.branches[name]
    branch = simulation.get_branch(name)
    if branch is not simulation:
        branch.branch_period = period
    return branch
