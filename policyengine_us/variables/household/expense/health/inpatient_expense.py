from policyengine_us.model_api import *


class inpatient_expense(Variable):
    value_type = float
    entity = Person
    label = "Inpatient expenses"
    unit = USD
    definition_period = YEAR
