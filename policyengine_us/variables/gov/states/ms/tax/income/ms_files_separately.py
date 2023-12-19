from policyengine_us.model_api import *


class ms_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on Mississippi tax return"
    definition_period = YEAR
    reference = ()
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        itax_indiv = add(tax_unit, period, ["ms_taxable_income_indiv"])
        itax_joint = tax_unit("ms_taxable_income_joint", period)
        return itax_indiv < itax_joint
