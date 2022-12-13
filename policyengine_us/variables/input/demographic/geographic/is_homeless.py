from policyengine_us.model_api import *


class is_homeless(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    documentation = "Whether all members are homeless individuals and are not receiving free shelter throughout the month"
    label = "Is homeless"
