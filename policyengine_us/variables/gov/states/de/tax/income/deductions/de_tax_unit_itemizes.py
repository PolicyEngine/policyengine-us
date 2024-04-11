from policyengine_us.model_api import *


class de_tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the tax unit in Delaware itemizes the deductions"
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        itemized_ded = tax_unit("de_itemized_deductions_unit", period)
        standard_ded = add(tax_unit, period, ["de_standard_deduction_indv"])
        return itemized_ded > standard_ded
