from policyengine_us.model_api import *


class ms_files_separately(Variable):
    value_type = bool
    entity = TaxUnit
    label = "married couple files separately on Mississippi tax return"
    definition_period = YEAR
    reference = (
    )
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        itax_indiv = tax_unit("ms_income_tax_indiv", period)
        itax_joint = tax_unit("ms_income_tax_joint", period)
        return itax_indiv < itax_joint
