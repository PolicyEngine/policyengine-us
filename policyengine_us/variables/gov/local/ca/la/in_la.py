from policyengine_us.model_api import *


class in_la(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Los Angeles County"
