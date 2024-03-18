from policyengine_us.model_api import *


class water_expense(Variable):
    value_type = float
    entity = Household
    label = "Water expense"
    unit = USD
    definition_period = YEAR
