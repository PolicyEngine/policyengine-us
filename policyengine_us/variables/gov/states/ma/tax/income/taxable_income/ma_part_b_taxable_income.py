from policyengine_us.model_api import *


class ma_part_b_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part B taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-3"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        part_b_agi = tax_unit("ma_part_b_agi", period)
        part_b_deductions = tax_unit(
            "ma_part_b_taxable_income_deductions", period
        )
        part_b_exemptions = tax_unit(
            "ma_part_b_taxable_income_exemptions", period
        )
        return max_(0, part_b_agi - part_b_deductions - part_b_exemptions)
