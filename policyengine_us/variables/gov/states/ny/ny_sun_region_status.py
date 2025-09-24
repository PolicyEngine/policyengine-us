from policyengine_us.model_api import *


class NySunRegion(Enum):
    LONG_ISLAND="Long Island"
    UPSTATE="Upstate"
    CON_ED="Con Ed"

class ny_sun_region_status(Variable):
    value_type = Enum
    entity = Household
    possible_values = NySunRegion
    defined_for = StateCode.NY
    definition_period = YEAR
    label = "residential status for NY SUN solar incentive"
    default_value = NySunRegion.UPSTATE

