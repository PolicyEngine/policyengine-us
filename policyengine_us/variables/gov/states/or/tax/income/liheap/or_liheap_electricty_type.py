from policyengine_us.model_api import *


class OregonLIHEAPElectricityType(Enum):
    HEATING = "Heating"
    COOLING = "Cooling"
    BOTH = "Both"


class or_liheap_electricity_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = OregonLIHEAPElectricityType
    default_value = OregonLIHEAPElectricityType.BOTH
    definition_period = YEAR
    label = "Electricity usage type for LIHEAP payout"
