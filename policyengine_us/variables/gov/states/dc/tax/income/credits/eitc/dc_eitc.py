from policyengine_us.model_api import *


class dc_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04"  # (f)
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        return where(
            tax_unit("eitc_child_count", period) > 0,
            tax_unit("dc_eitc_with_qualifying_child", period),
            tax_unit("dc_eitc_without_qualifying_child", period),
        )
