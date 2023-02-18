from policyengine_us.model_api import *


class tax_unit_children(Variable):
    value_type = float
    entity = TaxUnit
    label = "Number of children in tax unit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return add(tax_unit, period, ["is_child"])
