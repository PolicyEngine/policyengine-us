from policyengine_us.model_api import *


class non_deductible_mortgage_interest(Variable):
    value_type = float
    entity = Person
    label = "Non-deductible mortgage interest"
    unit = USD
    definition_period = YEAR
