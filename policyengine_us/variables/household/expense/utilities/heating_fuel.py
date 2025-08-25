from policyengine_us.model_api import *


class HeatingFuel(Enum):
    NONE = "None"
    ELECTRICITY = "Electricity"
    NATURAL_GAS = "Natural gas"
    OIL = "Oil"
    PROPANE = "Propane"
    KEROSENE = "Kerosene"
    WOOD = "Wood"
    COAL = "Coal"
    CORN = "Corn"
    PELLETS = "Pellets"
    OTHER = "Other"


class heating_fuel(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = HeatingFuel
    default_value = HeatingFuel.NATURAL_GAS
    definition_period = YEAR
    label = "Primary heating fuel type"
    documentation = "The primary fuel type used for heating the household"
    reference = (
        "https://www.eia.gov/consumption/residential/data/2020/hc/hc1.7.xlsx"
    )
