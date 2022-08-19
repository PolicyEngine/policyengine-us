from openfisca_us.model_api import *


class ma_part_b_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part B AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_b_gross_income = tax_unit("ma_part_b_gross_income", period)
        parameters = parameters(period).gov
        federal_deductions = parameters.irs.ald.deductions
        disallowed_deductions = parameters.states.ma.tax.income.ald.disallowed
        deductions = [
            deduction
            for deduction in federal_deductions
            if deduction not in disallowed_deductions
        ]
        deduction_value = add(tax_unit, period, deductions)
        return max_(0, part_b_gross_income - deduction_value)
