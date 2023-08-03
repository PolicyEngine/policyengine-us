from policyengine_us.model_api import *


class ma_part_b_taxable_income_before_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part B taxable income before exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_b_agi = tax_unit("ma_part_b_agi", period)
        part_b_deductions = tax_unit(
            "ma_part_b_taxable_income_deductions", period
        )
        return max_(0, part_b_agi - part_b_deductions)
