from policyengine_us.model_api import *


class household_refundable_local_tax_credits(Variable):
    value_type = float
    entity = Household
    label = "refundable local income tax credits"
    unit = USD
    definition_period = YEAR
    adds = ["nyc_refundable_credits"]
