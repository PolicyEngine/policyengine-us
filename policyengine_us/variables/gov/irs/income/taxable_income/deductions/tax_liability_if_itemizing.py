from policyengine_us.model_api import *


class tax_liability_if_itemizing(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability if itemizing"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        itemized_branch = get_itemization_branch(tax_unit, period, itemizes=True)
        return itemized_branch.calculate("income_tax", period)
