from policyengine_us.model_api import *


class cooling_expense(Variable):
    value_type = float
    entity = Person
    label = "Cooling cost for each person"
    unit = USD
    definition_period = YEAR
