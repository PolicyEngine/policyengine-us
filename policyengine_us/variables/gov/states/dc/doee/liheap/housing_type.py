from policyengine_us.model_api import *


class HousingType(Enum):
    SINGLE_FAMILY = "Single Family"
    MULTI_FAMILY = "Multi Family"


class housing_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = HousingType
    default_value = HousingType.SINGLE_FAMILY
    definition_period = YEAR
    label = "Housing types for LIHEAP payout"
