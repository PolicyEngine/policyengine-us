from openfisca_us.model_api import *


class irs_income_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "IRS taxable income deductions"
    unit = USD
    documentation = "Deductions from AGI to reach taxable income"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        deductions = parameters(
            period
        ).irs.deductions.taxable_income_deductions
        deduction_value = add(tax_unit, period, deductions)
        return max_(0, agi - deduction_value)
