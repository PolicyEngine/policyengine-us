from openfisca_us.model_api import *


class in_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "IN refundable credits"
    unit = USD
    definition_period = YEAR

    formula = sum_of_variables(
        [
            "in_state_tax_witheld",
            "in_county_tax_witheld",
            "in_earned_income_credit",
            "in_unified_elderly_credit",
            "in_other_refundable_credits",
        ]
    )
