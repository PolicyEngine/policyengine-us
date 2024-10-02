from policyengine_us.model_api import *


class ky_tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the tax unit in Kentucky itemizes the deductions when married filing separately"
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        itemized_ded = add(tax_unit, period, ["ky_itemized_deductions_indiv"])
        standard_ded = add(tax_unit, period, ["ky_standard_deduction_indiv"])
        return itemized_ded > standard_ded
