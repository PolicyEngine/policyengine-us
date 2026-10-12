from policyengine_us.model_api import *


class cbo_household_income_before_transfers_and_taxes(Variable):
    value_type = float
    entity = Household
    label = "CBO household income before transfers and taxes"
    documentation = (
        "CBO household income before transfers and taxes: market income plus "
        "social insurance benefits."
    )
    definition_period = YEAR
    unit = USD
    adds = [
        "cbo_household_market_income",
        "cbo_household_social_insurance_benefits",
    ]
