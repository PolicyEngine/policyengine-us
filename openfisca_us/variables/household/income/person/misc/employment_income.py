from policyengine_us.model_api import *


class employment_income(Variable):
    value_type = float
    entity = Person
    label = "Employment income"
    unit = USD
    definition_period = YEAR
