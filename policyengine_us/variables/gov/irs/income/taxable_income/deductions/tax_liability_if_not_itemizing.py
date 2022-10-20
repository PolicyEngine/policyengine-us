from policyengine_us.model_api import *
from policyengine_core.tracers import SimpleTracer


class tax_liability_if_not_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if not itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        non_itemized_branch = simulation.get_branch("not_itemizing")
        non_itemized_branch.set_input(
            "tax_unit_itemizes",
            period,
            np.zeros((tax_unit.count,), dtype=bool),
        )
        values = non_itemized_branch.calculate(
            "federal_state_income_tax", period
        )
        return values
