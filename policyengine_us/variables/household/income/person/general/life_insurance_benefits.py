from policyengine_us.model_api import *


class life_insurance_benefits(Variable):
    value_type = float
    entity = Person
    label = "Life insurance benefits"
    unit = USD
    documentation = (
        "Life insurance benefits and proceeds, including death benefit payments."
    )
    definition_period = YEAR
