from policyengine_us.model_api import *


class cooking_fuel_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Cooking fuel expense"
    unit = USD
    definition_period = YEAR
