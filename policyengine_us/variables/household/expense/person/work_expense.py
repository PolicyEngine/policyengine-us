from policyengine_us.model_api import *


class work_expense(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Work expenses"
