from policyengine_us.model_api import *


class in_yonkers(Variable):
    value_type = bool
    entity = Household
    label = "Resident of Yonkers, New York"
    documentation = (
        "Whether the household resides in the city of Yonkers. Yonkers does "
        "not align with a county, so it is provided as an input."
    )
    definition_period = YEAR
