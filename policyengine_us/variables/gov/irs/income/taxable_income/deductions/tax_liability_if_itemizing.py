from policyengine_us.model_api import *
from policyengine_core.simulations import Simulation


class tax_liability_if_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation: Simulation = tax_unit.simulation
        itemized_branch = simulation.get_branch("itemizing")
        itemized_branch.set_input(
            "tax_unit_itemizes", period, np.ones((tax_unit.count,), dtype=bool)
        )
        values = itemized_branch.calculate("federal_state_income_tax", period)
        del simulation.branches["itemizing"]
        return values
