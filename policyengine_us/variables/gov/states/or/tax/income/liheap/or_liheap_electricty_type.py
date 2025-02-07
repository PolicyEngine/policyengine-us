from policyengine_us.model_api import *


class ElectricityUsageType(Enum):
    HEATING = "Heating"
    COOLING = "Cooling"
    BOTH = "Both"

class electricity_usage_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = ElectricityUsageType
    default_value = ElectricityUsageType.BOTH  
    definition_period = YEAR
    label = "Electricity usage type for LIHEAP payout"

