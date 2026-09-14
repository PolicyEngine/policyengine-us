from policyengine_us.model_api import *


class veterans_benefits(Variable):
    value_type = float
    entity = Person
    label = "Veterans benefits"
    unit = USD
    documentation = "Veterans benefits from past military service."
    definition_period = YEAR
