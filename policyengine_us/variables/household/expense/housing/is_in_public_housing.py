from policyengine_us.model_api import *


class is_in_public_housing(Variable):
    value_type = bool
    entity = Household
    label = "Whether the household is in public housing"
    definition_period = YEAR
