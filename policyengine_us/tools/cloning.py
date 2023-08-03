from policyengine_core.simulations import Simulation


def get_stored_variables(simulation: Simulation) -> list:
    stored_variables = []
    for variable in simulation.tax_benefit_system.variables:
        holder = simulation.get_holder(variable)
        if len(holder.get_known_periods()) > 0:
            stored_variables.append(variable)
    return stored_variables
