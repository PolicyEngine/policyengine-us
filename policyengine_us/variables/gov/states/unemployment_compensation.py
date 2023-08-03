from policyengine_us.model_api import *


class unemployment_compensation(Variable):
    value_type = float
    entity = Person
    label = "unemployment compensation"
    unit = USD
    documentation = "Income from unemployment compensation programs."
    definition_period = YEAR
