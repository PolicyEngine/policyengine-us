from policyengine_us.model_api import *


class household_net_income(Variable):
    value_type = float
    entity = Household
    label = "net income"
    definition_period = YEAR
    unit = USD
    adds = [
        "household_market_income",
        "household_benefits",
        "household_refundable_tax_credits",
    ]
    subtracts = ["household_tax_before_refundable_credits"]
