from openfisca_us.model_api import *


class taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "IRS taxable income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        deductions = tax_unit("taxable_income_deductions", period)
        return max_(0, agi - deductions)
