from policyengine_us.model_api import *


class in_wilmington(Variable):
    value_type = bool
    entity = Household
    label = "Resident of Wilmington, Delaware"
    definition_period = YEAR
