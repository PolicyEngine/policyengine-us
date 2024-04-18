from policyengine_us.model_api import *


class ms_income_tax_before_credits_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi income tax before credits"
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
        return where(ms_files_separately, itax_indiv, itax_joint)
