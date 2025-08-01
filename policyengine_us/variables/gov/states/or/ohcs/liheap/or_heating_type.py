from policyengine_us.model_api import *


class ORHeatingType(Enum):
    ELECTRICITY = "Electricity"
    HEATING_OIL = "Heating Oil"
    LIQUID_GAS = "Liquid Gas"
    NATURAL_GAS = "Natural Gas"
    WOOD_PELLETS = "Wood Pellets"


class or_heating_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = ORHeatingType
    default_value = ORHeatingType.ELECTRICITY
    definition_period = YEAR
    label = "Household Heating type"
