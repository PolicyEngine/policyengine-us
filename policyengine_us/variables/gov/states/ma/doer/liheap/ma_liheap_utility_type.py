from policyengine_us.model_api import *


class MassachusettsLIHEAPUtilityType(Enum):
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
    possible_values = MassachusettsLIHEAPUtilityType
    default_value = MassachusettsLIHEAPUtilityType.ELECTRICITY
    definition_period = YEAR
    defined_for = StateCode.MA
    label = "Massachusetts LIHEAP Household Utility type"
