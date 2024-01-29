from policyengine_us.model_api import *


class va_low_income_tax_credit_agi_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Virginia low income tax credit"
    definition_period = YEAR
    defined_for = "va_low_income_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        agi = tax_unit("va_agi", period)
        # Virginia does not account for blind or aged exemptions
        fpg = tax_unit("tax_unit_fpg", period)
        return agi <= fpg
