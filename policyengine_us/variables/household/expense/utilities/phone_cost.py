from policyengine_us.model_api import *


class phone_cost(Variable):
    value_type = float
    entity = Household
    label = "Phone cost"
    unit = USD
    definition_period = YEAR
