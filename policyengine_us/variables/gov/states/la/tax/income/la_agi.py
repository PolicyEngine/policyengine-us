from policyengine_us.model_api import *


class la_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana adjusted gross income income"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        exempt_income = tax_unit("la_agi_exempt_income", period)
        return max_(agi - exempt_income, 0)
