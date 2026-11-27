from policyengine_core.populations import Population
from policyengine_core.simulations import Simulation


def get_stored_variables(simulation: Simulation) -> list:
    stored_variables = []
    for variable in simulation.tax_benefit_system.variables:
        holder = simulation.get_holder(variable)
        if len(holder.get_known_periods()) > 0:
            stored_variables.append(variable)
    return stored_variables


def get_branch_to_change(
    simulation: Simulation, branch_name: str, clone_system: bool = False
) -> Simulation:
    """Return ``simulation.get_branch(branch_name)``, never ``simulation``.

    For a formula that changes its branch's inputs or tax-benefit system.
    ``get_branch`` returns the simulation itself when asked for the
    simulation's own branch name, so the formula would change the simulation
    it is calculating and give a wrong result. Raise ``ValueError`` instead,
    before anything changes.
    """
    branch = simulation.get_branch(branch_name, clone_system=clone_system)
    if branch is simulation:
        raise ValueError(
            f"This simulation is the branch {branch_name!r}, the name the"
            " formula gives the branch it changes. Calculate it in a"
            " simulation with another branch name."
        )
    return branch


class BranchedSimulation:
    def __init__(self, population: Population):
        self.simulation = population.simulation

    def __enter__(self):
        simulation = self.simulation.clone()
        simulation.max_spiral_loops = 10
        simulation._check_for_cycle = lambda *args: None
        self.computed_variables = get_stored_variables(simulation)
        simulation.tracer = self.simulation.tracer
        self.branched_simulation: Simulation = simulation

        return self.branched_simulation

    def __exit__(self, type, value, traceback):
        added_variables = set(get_stored_variables(self.branched_simulation)) - set(
            self.computed_variables
        )
        for variable in added_variables:
            self.simulation.get_holder(variable).delete_arrays()
