from policyengine_us.model_api import *


class outpatient_expense(Variable):
    value_type = float
    entity = Person
    label = "Outpatient expenses"
    unit = USD
    definition_period = YEAR
