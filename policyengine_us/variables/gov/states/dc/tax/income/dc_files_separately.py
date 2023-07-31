from policyengine_us.model_api import *


class dc_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Married couple files separately on DC tax return"
    definition_period = YEAR
    reference = ()
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        itax_indiv = tax_unit("dc_income_tax_before_credits_indiv", period)
        itax_joint = tax_unit("dc_income_tax_before_credits_joint", period)
        return itax_indiv < itax_joint
