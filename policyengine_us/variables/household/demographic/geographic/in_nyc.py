from policyengine_us.model_api import *


class in_nyc(Variable):
    value_type = bool
    entity = Household
    definition_period = ETERNITY
    label = "Is in NYC"