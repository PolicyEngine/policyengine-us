from policyengine_us.model_api import *


class mt_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on Montana tax return"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        itax_indiv = add(tax_unit, period, ["mt_income_tax_indiv"])
        itax_joint = tax_unit("mt_income_tax_joint", period)
        return itax_indiv < itax_joint
