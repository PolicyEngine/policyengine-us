from policyengine_us.model_api import *


class small_area_fair_market_rent(Variable):
    value_type = float
    entity = Household
    label = "Small area fair market rent"
    unit = USD
    definition_period = YEAR
