from policyengine_us.model_api import *


class care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Care expenses"
    unit = USD
    definition_period = MONTH
