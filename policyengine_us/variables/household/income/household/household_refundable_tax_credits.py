from policyengine_us.model_api import *


class household_refundable_tax_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable tax credits"
    definition_period = YEAR
    unit = USD
    adds = [
        "income_tax_refundable_credits",  # Federal.
        "ma_refundable_credits",  # Massachusetts.
        "md_refundable_credits",  # Maryland.
        "or_refundable_credits",  # Oregon.
        "ny_refundable_credits",  # New York.
        # Skip PA, which has no refundable credits.
    ]
