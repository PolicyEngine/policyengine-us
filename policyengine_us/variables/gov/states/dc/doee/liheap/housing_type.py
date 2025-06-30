from policyengine_us.model_api import *


class HousingType(Enum):
    SF = "Single Family"
    MF = "Multi Family"


class housing_type(Variable):
    value_type = Enum
    entity = Household
    possible_values = HousingType
    default_value = HousingType.SF
    definition_period = YEAR
    label = "Housing types for LIHEAP payout"
