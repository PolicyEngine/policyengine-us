from policyengine_us.model_api import *


class investment_interest(Variable):
    value_type = float
    entity = Person
    label = "Investment interest"
    unit = USD
    definition_period = YEAR
