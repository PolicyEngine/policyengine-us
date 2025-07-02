from policyengine_us.model_api import *


class household_market_income(Variable):
    value_type = float
    entity = Household
    label = "market income"
    documentation = "Income from non-government sources."
    definition_period = YEAR
    unit = USD

    adds = "gov.household.market_income_sources"
