from policyengine_us.model_api import *


class ms_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on Mississippi tax return"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        itax_indiv = add(
            tax_unit, period, ["ms_income_tax_before_credits_indiv"]
        )
        itax_joint = add(
            tax_unit, period, ["ms_income_tax_before_credits_joint"]
        )
        return itax_indiv < itax_joint
