from policyengine_us.model_api import *


class personal_interest_expense(Variable):
    value_type = float
    entity = Person
    label = "Personal interest expense"
    unit = USD
    definition_period = YEAR
