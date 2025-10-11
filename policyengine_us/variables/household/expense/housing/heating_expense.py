from policyengine_us.model_api import *


class heating_expense(Variable):
    value_type = float
    entity = Person
    label = "Heating cost for each person"
    unit = USD
    definition_period = YEAR
