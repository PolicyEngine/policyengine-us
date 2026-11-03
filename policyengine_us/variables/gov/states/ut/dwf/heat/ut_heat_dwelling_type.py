from policyengine_us.model_api import *


class UtHeatDwellingType(Enum):
    APARTMENT = "Apartment, condominium, townhouse, or small trailer home"
    HOUSE = "House, mobile home, basement apartment, or duplex"


class ut_heat_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = UtHeatDwellingType
    default_value = UtHeatDwellingType.HOUSE
    definition_period = YEAR
    label = "Utah HEAT dwelling category"
    defined_for = StateCode.UT
    reference = "https://jobs.utah.gov/infosource/heatpolicy/Policy/600_Payment_Calculation/609_Table_III_Monthly_Energy_Cost_Standards.htm"
