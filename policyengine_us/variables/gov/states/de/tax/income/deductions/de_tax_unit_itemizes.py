from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import state_itemization_uses_itemized


class de_tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the tax unit in Delaware itemizes the deductions"
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        itemized_ded = tax_unit("de_itemized_deductions_unit", period)
        standard_ded = add(tax_unit, period, ["de_standard_deduction_indv"])
        method = tax_unit("state_deduction_method", period)
        return state_itemization_uses_itemized(method, itemized_ded > standard_ded)
