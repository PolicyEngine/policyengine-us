from policyengine_us.model_api import *


class in_wilmington(Variable):
    value_type = bool
    entity = Household
    label = "Resident of Wilmington, Delaware"
    documentation = (
        "Whether the household resides in the city of Wilmington. Wilmington "
        "does not align with a county, so it is provided as an input."
    )
    definition_period = YEAR
