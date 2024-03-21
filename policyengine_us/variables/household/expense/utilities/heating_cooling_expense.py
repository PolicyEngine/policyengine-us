from policyengine_us.model_api import *


class heating_cooling_expense(Variable):
    value_type = float
    entity = Household
    label = "Heating and cooling expense"
    unit = USD
    definition_period = YEAR
