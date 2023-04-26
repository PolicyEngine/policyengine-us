from policyengine_us.model_api import *


class state_fips(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    documentation = "State FIPS code"
    default_value = 6
