from policyengine_us.model_api import *


class total_income(Variable):
    value_type = float
    entity = Person
    label = "state or federal salary"
    unit = USD
    definition_period = YEAR
