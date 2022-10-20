from policyengine_core.populations import Population
from policyengine_core.simulations import Simulation


def get_stored_variables(simulation: Simulation) -> list:
    stored_variables = []
    for variable in simulation.tax_benefit_system.variables:
        holder = simulation.get_holder(variable)
        if len(holder.get_known_periods()) > 0:
            stored_variables.append(variable)
    return stored_variables


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
        added_variables = set(
            get_stored_variables(self.branched_simulation)
        ) - set(self.computed_variables)
        for variable in added_variables:
            self.simulation.get_holder(variable).delete_arrays()
