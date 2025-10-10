from policyengine_us.model_api import *


class transportation_expense(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Transportation expense"
    unit = USD
