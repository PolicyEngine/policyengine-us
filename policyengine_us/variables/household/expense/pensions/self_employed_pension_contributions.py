from policyengine_us.model_api import *


class self_employed_pension_contributions(Variable):
    value_type = float
    entity = Person
    label = "Self-employed pension contributions"
    unit = USD
    documentation = "Pension plan contributions associated with plans for the self employed."
    definition_period = YEAR
