from policyengine_us.model_api import *


class va_low_income_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Virginia low income tax credit"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        fpg = tax_unit("tax_unit_fpg", period)
        agi = tax_unit("va_agi", period)
        return agi <= fpg
