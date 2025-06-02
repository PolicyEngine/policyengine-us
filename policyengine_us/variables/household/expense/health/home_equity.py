from policyengine_us.model_api import *

class home_equity(Variable):
    value_type = float
    entity = Household
    label = "Cost of House"
    definition_period = YEAR
    unit = USD