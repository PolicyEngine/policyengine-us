from policyengine_us.model_api import *


class other_miscellaneous_expenses(Variable):
    value_type = float
    entity = Person
    label = "Other miscellaneous expenses"
    unit = USD
    definition_period = YEAR
