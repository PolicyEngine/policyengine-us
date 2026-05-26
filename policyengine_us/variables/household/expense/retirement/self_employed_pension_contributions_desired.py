from policyengine_us.model_api import *


class self_employed_pension_contributions_desired(Variable):
    value_type = float
    entity = Person
    label = "Desired self-employed pension contributions"
    unit = USD
    documentation = (
        "Self-employed pension plan contributions before statutory contribution limits."
    )
    definition_period = YEAR
