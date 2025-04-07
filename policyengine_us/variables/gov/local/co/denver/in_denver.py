from policyengine_us.model_api import *


class in_denver(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Is in Denver County"
