from policyengine_us.model_api import *


class vehicle_mortgage_expense(Variable):
    value_type = float
    entity = Person
    label = "Vehivle mortgage expense"
    unit = USD
    definition_period = YEAR
