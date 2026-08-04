from policyengine_us.model_api import *


class is_shared_living(Variable):
    value_type = bool
    entity = Household
    label = "Whether the household is a shared living arrangement"
    definition_period = YEAR
