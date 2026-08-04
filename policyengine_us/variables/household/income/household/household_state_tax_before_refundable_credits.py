from policyengine_us.model_api import *


class household_state_tax_before_refundable_credits(Variable):
    value_type = float
    entity = Household
    label = "household State tax before refundable credits"
    unit = USD
    definition_period = YEAR
    adds = ["state_income_tax_before_refundable_credits", "state_use_tax"]
