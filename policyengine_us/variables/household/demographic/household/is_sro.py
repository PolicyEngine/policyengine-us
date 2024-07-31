from policyengine_us.model_api import *


class is_sro(Variable):
    value_type = bool
    entity = Household
    label = "Is single room occupancy"
    definition_period = YEAR
