from policyengine_us.model_api import *


class tax_unit_state(Variable):
    value_type = str
    entity = TaxUnit
    label = "Tax unit State"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit.household("state_code_str", period)
