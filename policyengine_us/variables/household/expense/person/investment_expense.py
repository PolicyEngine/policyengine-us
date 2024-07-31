from policyengine_us.model_api import *


class investment_expenses(Variable):
    value_type = float
    entity = Person
    label = "Investment expenses"
    unit = USD
    definition_period = YEAR
