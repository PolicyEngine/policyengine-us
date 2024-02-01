from policyengine_us.model_api import *


class de_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        de_agi = tax_unit("de_agi", period)
        de_deductions = tax_unit("de_deductions", period)
        return max_(de_agi - de_deductions, 0)
