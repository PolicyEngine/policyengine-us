from policyengine_us.model_api import *


class ccdf_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Income"
    definition_period = YEAR
    unit = USD
    adds = ["market_income"]
