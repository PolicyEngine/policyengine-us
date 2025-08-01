from policyengine_us.model_api import *


class DCLIHEAPHeatingType(Enum):
    ELECTRICITY = "Electricity"
    GAS = "Gas"
    HEAT_IN_RENT = "Heat in Rent"  # Electricity or gas included in rent
    OIL = "Oil"


class dc_liheap_heating_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = DCLIHEAPHeatingType
    default_value = DCLIHEAPHeatingType.ELECTRICITY
    definition_period = YEAR
    label = "Household heating types for DC LIHEAP"
