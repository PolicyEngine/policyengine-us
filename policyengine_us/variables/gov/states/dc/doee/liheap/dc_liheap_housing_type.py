from policyengine_us.model_api import *


class DCLIHEAPHousingType(Enum):
    SINGLE_FAMILY = "Single Family"
    MULTI_FAMILY = "Multi Family"


class dc_liheap_housing_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = DCLIHEAPHousingType
    default_value = DCLIHEAPHousingType.SINGLE_FAMILY
    definition_period = YEAR
    label = "Housing types for LIHEAP payout"
