from policyengine_us.model_api import *


class poverty_gap(Variable):
    label = "poverty gap"
    documentation = "Poverty gap"
    entity = Household
    definition_period = YEAR
    value_type = float
    unit = USD
