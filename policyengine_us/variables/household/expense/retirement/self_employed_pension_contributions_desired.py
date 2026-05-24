from policyengine_us.model_api import *


class self_employed_pension_contributions_desired(Variable):
    value_type = float
    entity = Person
    label = "Desired self-employed pension contributions"
    unit = USD
    documentation = (
        "Self-employed pension contributions before applying statutory limits."
    )
    definition_period = YEAR
