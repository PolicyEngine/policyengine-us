from openfisca_us.model_api import *


class ma_part_b_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA Part B gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.mass.gov/info-details/mass-general-laws-c62-ss-2"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        ma_gross_income = tax_unit("ma_gross_income", period)
        ma_part_a_gross_income = tax_unit("ma_part_a_gross_income", period)
        ma_part_c_gross_income = tax_unit("ma_part_c_gross_income", period)
        return (
            ma_gross_income - ma_part_a_gross_income - ma_part_c_gross_income
        )
