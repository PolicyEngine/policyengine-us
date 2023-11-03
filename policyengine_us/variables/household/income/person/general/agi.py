from policyengine_us.model_api import *


class net_income(Variable):
    value_type = float
    entity = Person
    label = "Adjusted gross income"
    unit = USD
    documentation = "Personal adjusted gross income"
    definition_period = YEAR
