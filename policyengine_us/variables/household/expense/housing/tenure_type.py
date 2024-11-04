from policyengine_us.model_api import *


class TenureType(Enum):
    RENTED = "rented"
    OWNED_OUTRIGHT = "owned outright"
    OWNED_WITH_MORTGAGE = "owned with mortgage"
    NONE = "none"


class tenure_type(Variable):
    value_type = Enum
    entity = Household
    possible_values = TenureType
    default_value = TenureType.NONE
    label = "tenure type"
    definition_period = YEAR
