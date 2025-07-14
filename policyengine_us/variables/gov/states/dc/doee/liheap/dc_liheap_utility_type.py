from policyengine_us.model_api import *


class DCLIHEAPUtilityType(Enum):
    ELECTRICITY = "Electricity"
    GAS = "Gas"
    HEAT_IN_RENT = "Heat in Rent"  # Electricity or gas included in rent
    OIL = "Oil"


class dc_liheap_utility_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = DCLIHEAPUtilityType
    default_value = DCLIHEAPUtilityType.ELECTRICITY
    definition_period = YEAR
    label = "Household utility types for DC LIHEAP"
