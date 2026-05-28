from policyengine_us.model_api import *


class medicaid_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Medicaid cost if enrolled"
    unit = USD
    definition_period = YEAR
