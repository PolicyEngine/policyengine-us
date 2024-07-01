from policyengine_us.model_api import *


class RegionStatus(Enum):
    LONG_ISLAND="Long Island"
    UPSTATE="Upstate"
    CON_ED="Con Ed"

class ny_sun_region_status(Variable):
    value_type = Enum
    entity = TaxUnit
    possible_values = RegionStatus
    definition_period = YEAR
    label = "residential status for solar incentive"
    default_value = RegionStatus.UPSTATE

#trying to fill out formula like in filing_status py file
#unsure how to replace tax unit with household
#Current error:     You tried to calculate or to set a value for variable 'region_incentive', 
#but it was not found in the loaded tax and benefit system (CountryTaxBenefitSystem).
def formula(tax_unit, period, parameters):
    person = tax_unit.members
    is_separated = tax_unit.any(person("is_separated", period))
    return select(
 
        [
            RegionStatus.LONG_ISLAND,
            RegionStatus.UPSTATE,
            RegionStatus.CON_ED,
        ],
        default=RegionStatus.UPSTATE,
    )

