from policyengine_us.model_api import *


class in_yonkers(Variable):
    value_type = bool
    entity = Household
    label = "Resident of Yonkers, New York"
    definition_period = YEAR
