from policyengine_us.model_api import *


class in_poverty(Variable):
    label = "in poverty"
    documentation = "Whether household is in poverty"
    entity = Household
    definition_period = YEAR
    value_type = bool
    adds = ["spm_unit_is_in_spm_poverty"]
