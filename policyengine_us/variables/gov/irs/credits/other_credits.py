from policyengine_us.model_api import *


class other_credits(Variable):
    value_type = float
    entity = Person
    label = "other credits"
    unit = USD
    definition_period = YEAR
