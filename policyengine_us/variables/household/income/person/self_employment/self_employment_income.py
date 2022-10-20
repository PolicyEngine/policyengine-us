from policyengine_us.model_api import *


class self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "Self-employment income"
    unit = USD
    documentation = "Self-employment non-farm income."
    definition_period = YEAR
