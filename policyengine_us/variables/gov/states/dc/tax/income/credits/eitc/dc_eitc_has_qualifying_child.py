from policyengine_us.model_api import *


class dc_eitc_has_qualifying_child(Variable):
    value_type = bool
    entity = TaxUnit
    label = "DC EITC Without Qualifying Child Amount"
    unit = USD
    definition_period = YEAR
    reference = "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.04"  # (f)
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        qualifying = person("is_eitc_qualifying_child", period)

        return tax_unit.sum(qualifying)