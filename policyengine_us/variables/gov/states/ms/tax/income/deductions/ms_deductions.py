from policyengine_us.model_api import *


class ms_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        itemized = tax_unit("ms_itemized_deductions", period)
        standard = tax_unit("ms_standard_deduction", period)
        return max_(itemized, standard)
