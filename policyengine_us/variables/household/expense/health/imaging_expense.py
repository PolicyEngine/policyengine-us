from policyengine_us.model_api import *


class imaging_expense(Variable):
    value_type = float
    entity = Person
    label = "Imaging expenses"
    unit = USD
    definition_period = YEAR
