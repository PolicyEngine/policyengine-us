from policyengine_us.model_api import *


class cbo_household_income(Variable):
    value_type = float
    entity = Household
    label = "CBO household income"
    documentation = (
        "CBO household income, which by default refers to income before "
        "means-tested transfers and federal taxes."
    )
    definition_period = YEAR
    unit = USD
    adds = ["cbo_household_income_before_transfers_and_taxes"]
