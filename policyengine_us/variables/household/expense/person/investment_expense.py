from policyengine_us.model_api import *


class investment_expense(Variable):
    value_type = float
    entity = Person
    label = "Investment expense"
    unit = USD
    definition_period = YEAR
