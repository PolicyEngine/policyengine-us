from policyengine_us.model_api import *


class UtilityType(Enum):
    ELECTRIC = "Electric"
    GAS = "Gas"
    HIR = "Hir"
    OIL = "Oil"


class utility_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = UtilityType
    default_value = UtilityType.ELECTRIC
    definition_period = YEAR
    label = "Utility types for LIHEAP payout"

