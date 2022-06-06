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

        simulation_if_not_itemizing = simulation.clone()
        simulation_if_not_itemizing.tracer = SimpleTracer()
        simulation_if_not_itemizing.set_input(
            "tax_unit_itemizes",
            period,
            np.zeros((tax_unit.count,), dtype=bool),
        )
        old_tracer = simulation.tracer
        simulation.tracer = SimpleTracer()
        # This fixes a memory bug, essentially taking
        # the tracer out of reach of the new simulation (which somehow pollutes the old one)
        try:
            values = simulation_if_not_itemizing.calculate(
                "federal_state_income_tax", period
            )
        except Exception as e:
            simulation.tracer = old_tracer
            raise e
        simulation.tracer = old_tracer  # Re-attach the old tracer
        return values
