from openfisca_us.model_api import *
from openfisca_core.tracers import FullTracer


class tax_liability_if_not_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if not itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation

        simulation_if_not_itemizing = simulation.clone()
        simulation_if_not_itemizing.tracer = FullTracer()
        simulation_if_not_itemizing.set_input(
            "tax_unit_itemizes", period, False
        )
        old_tracer = simulation.tracer
        simulation.tracer = FullTracer()
        values = simulation_if_not_itemizing.calculate(
            "total_income_tax", period
        )
        simulation.tracer = old_tracer
        return values
