from policyengine_us.model_api import *


class UtilityType(Enum):
    DELIVERABLE_FUEL = "Deliverable Fuel"
    UTILITY_AND_HEAT_IN_RENT = "Utility and Heat in Rent"
    HEC = "HEC"
    HEATING_OIL_AND_PROPANE = "Heating oil and Propane"
    NATURAL_GAS = "Natural Gas"
    OTHER = "Other"
    KEROSENE = "Kerosene"
    ELECTRICITY = "Electricity"


class ma_liheap_utility_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = UtilityType
    default_value = UtilityType.ELECTRICITY
    definition_period = YEAR
    label = "Household Utility type"
