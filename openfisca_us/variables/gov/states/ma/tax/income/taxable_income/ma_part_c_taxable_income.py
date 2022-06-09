from openfisca_us.model_api import *


class ma_part_c_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part C taxable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-3"

    def formula(tax_unit, period, parameters):
        part_a_agi = tax_unit("ma_part_a_agi", period)
        part_b_agi = tax_unit("ma_part_b_agi", period)
        part_c_agi = tax_unit("ma_part_c_agi", period)
        part_b_deductions = tax_unit(
            "ma_part_b_taxable_income_deductions", period
        )
        remaining_part_b_deductions = max_(
            0, part_b_deductions - part_b_agi - part_a_agi
        )
        return max_(0, part_c_agi - remaining_part_b_deductions)
