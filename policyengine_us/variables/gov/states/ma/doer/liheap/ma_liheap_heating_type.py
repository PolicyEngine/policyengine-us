from policyengine_us.model_api import *


class MassachusettsLIHEAPHeatingType(Enum):
    HEATING_OIL_AND_PROPANE = "Heating oil and Propane"
    NATURAL_GAS = "Natural Gas"
    KEROSENE = "Kerosene"
    ELECTRICITY = "Electricity"
    OTHER = "Other"


class ma_liheap_heating_type(Variable):
    value_type = Enum
    entity = Household
    possible_values = MassachusettsLIHEAPHeatingType
    default_value = MassachusettsLIHEAPHeatingType.ELECTRICITY
    definition_period = YEAR
    defined_for = StateCode.MA
    label = "Massachusetts LIHEAP Household Heating type"
