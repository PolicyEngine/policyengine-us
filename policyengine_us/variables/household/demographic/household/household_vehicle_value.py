from policyengine_us.model_api import *


class household_vehicles_value(Variable):
    value_type = float
    entity = Household
    label = "Value of vehicles owned"
    definition_period = YEAR
