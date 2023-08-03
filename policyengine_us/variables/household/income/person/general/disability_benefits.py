from policyengine_us.model_api import *


class disability_benefits(Variable):
    value_type = float
    entity = Person
    label = "disability benefits"
    unit = USD
    documentation = "Disability benefits from employment (not Social Security), except for worker's compensation."
    definition_period = YEAR
