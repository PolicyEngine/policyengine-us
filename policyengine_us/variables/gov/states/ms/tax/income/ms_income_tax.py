from policyengine_us.model_api import *


class ms_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        ms_files_separately = tax_unit("ms_files_separately", period)
        itax_indiv = add(
            tax_unit, period, ["ms_income_tax_before_credits_indiv"]
        )
        itax_joint = add(
            tax_unit, period, ["ms_income_tax_before_credits_joint"]
        )
        tax_before_credits = where(ms_files_separately, itax_indiv, itax_joint)
        non_refundable_credits = tax_unit("ms_non_refundable_credits", period)
        return max_(tax_before_credits - non_refundable_credits, 0)
