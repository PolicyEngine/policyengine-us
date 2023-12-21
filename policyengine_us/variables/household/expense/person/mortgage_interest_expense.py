from policyengine_us.model_api import *


class mortgage_interest_expense(Variable):
    value_type = float
    entity = Person
    label = "Mortgage interest expense"
    unit = USD
    definition_period = YEAR
