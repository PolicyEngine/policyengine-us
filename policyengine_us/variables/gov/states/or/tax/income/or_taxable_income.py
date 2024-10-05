from policyengine_us.model_api import *


class or_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        or_agi = tax_unit("or_agi", period)
        deductions = tax_unit("or_deductions", period)
        return max_(or_agi - deductions, 0)
