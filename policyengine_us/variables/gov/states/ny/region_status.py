from policyengine_us.model_api import *


class RegionStatus(Enum):
    LONG_ISLAND="Long Island"
    UPSTATE="Upstate"
    CON_ED="Con Ed"

class ny_sun_region_status(Variable):
    value_type = Enum
    entity = Household
    possible_values = RegionStatus
    defined_for = StateCode.NY
    definition_period = YEAR
    label = "residential status for solar incentive"
    default_value = RegionStatus.UPSTATE

#trying to fill out formula like in filing_status py file
#unsure how to replace tax unit with household
#Current error:     You tried to calculate or to set a value for variable 'region_incentive', 
#but it was not found in the loaded tax and benefit system (CountryTaxBenefitSystem).

