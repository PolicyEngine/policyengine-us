from policyengine_us.model_api import *


class DCLIHEAPHousingType(Enum):
    SINGLE_FAMILY = "Single Family"
    MULTI_FAMILY = "Multi Family"


class dc_liheap_housing_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = DCLIHEAPHousingType
    default_value = DCLIHEAPHousingType.MULTI_FAMILY
    definition_period = YEAR
    label = "Housing type for DC LIHEAP"
