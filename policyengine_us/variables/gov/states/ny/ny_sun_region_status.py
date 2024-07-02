from policyengine_us.model_api import *


class NySunRegion(Enum):
    LONG_ISLAND="Long Island"
    UPSTATE="Upstate"
    CON_ED="Con Ed"

class ny_sun_regionVariable):
    value_type = Enum
    entity = Household
    possible_values = RegionStatus
    defined_for = StateCode.NY
    definition_period = YEAR
    label = "residential status for NY SUN solar incentive"
    default_value = RegionStatus.UPSTATE

