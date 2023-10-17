from policyengine_us.model_api import *


class de_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        sd = tax_unit("de_standard_deduction", period)
        id = tax_unit("de_itemized_deductions", period)
        return max_(sd, id)
