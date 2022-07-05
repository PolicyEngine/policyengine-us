from re import sub
from openfisca_us.model_api import *


class va_adjusted_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "VA adjusted gross income"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        additions = tax_unit("va_income_additions", period)
        age_deduction = tax_unit("va_age_deduction", period)
        ss_railroad_ben = 0  # social security and railroad benefits holder
        salt_refund = tax_unit("salt_refund_last_year")
        subtractions = tax_unit("va_income_subtractions", period)

        return (
            agi
            + additions
            - age_deduction
            - ss_railroad_ben
            - salt_refund
            - subtractions
        )
