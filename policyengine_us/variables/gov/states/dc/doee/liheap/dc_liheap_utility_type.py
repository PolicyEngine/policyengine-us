from policyengine_us.model_api import *


class DCLIHEAPUtilityType(Enum):
    ELECTRIC = "Electric"
    GAS = "Gas"
    VENDOR_ELECTRIC = "Vendor Electric"
    VENDOR_GAS = "Vendor Gas"
    HEAT_IN_RENT = "Heat in Rent"  # Electric or gas included in rent
    OIL = "Oil"


class dc_liheap_utility_type(Variable):
    value_type = Enum
    entity = Household
    possible_values = DCLIHEAPUtilityType
    default_value = DCLIHEAPUtilityType.ELECTRIC
    definition_period = YEAR
    label = "Household utility types for DC LIHEAP"
