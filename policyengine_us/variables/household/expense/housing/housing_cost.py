from policyengine_us.model_api import *


class housing_cost(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing cost"
    unit = USD
    definition_period = YEAR

    adds = ["rent"]
