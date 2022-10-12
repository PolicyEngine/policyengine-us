from policyengine_us.model_api import *


class alimony_expense(Variable):
    value_type = float
    entity = Person
    label = "Alimony expense"
    unit = USD
    definition_period = YEAR
