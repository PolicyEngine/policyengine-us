from openfisca_us.model_api import *
from openfisca_core.tracers import SimpleTracer


class tax_liability_if_not_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if not itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        simulation.max_spiral_loops = 10
        simulation._check_for_cycle = lambda *args: None
        simulation_if_not_itemizing = simulation.clone()
        computed_variables = get_stored_variables(simulation)
        simulation_if_not_itemizing.tracer = simulation.tracer
        simulation_if_not_itemizing.set_input(
            "tax_unit_itemizes",
            period,
            np.zeros((tax_unit.count,), dtype=bool),
        )
        values = simulation_if_not_itemizing.calculate(
            "federal_state_income_tax", period
        )
        added_variables = set(
            get_stored_variables(simulation_if_not_itemizing)
        ) - set(computed_variables)
        for variable in added_variables:
            simulation.get_holder(variable).delete_arrays()
        return values
