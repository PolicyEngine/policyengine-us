from policyengine_us.model_api import *


class tax_liability_if_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        simulation = tax_unit.simulation
        itemized_branch = simulation.get_branch("itemizing")
        itemized_branch.set_input(
            "tax_unit_itemizes", period, np.ones((tax_unit.count,), dtype=bool)
        )
        return itemized_branch.calculate("income_tax", period)
