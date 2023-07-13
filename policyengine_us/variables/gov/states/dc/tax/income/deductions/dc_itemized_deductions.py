from policyengine_us.model_api import *


class dc_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC itemized deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        return 0
