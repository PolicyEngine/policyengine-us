from policyengine_us.model_api import *


class household_income_tax_refundable_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable credits"
    definition_period = YEAR
    unit = USD
    adds = [
        "income_tax_refundable_credits",  # Federal.
        "or_refundable_credits",  # Oregon.
    ]
