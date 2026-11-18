from policyengine_us.model_api import *


class WIWHEAPDwellingType(Enum):
    SINGLE_FAMILY = "Single family"
    TWO_TO_FOUR_UNITS = "2- to 4-unit building"
    APARTMENT = "Apartment or multi-unit building"
    MOBILE_HOME = "Mobile home"
    MOTEL_OR_CAMPER = "Motel or camper/RV"


class wi_wheap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = WIWHEAPDwellingType
    default_value = WIWHEAPDwellingType.SINGLE_FAMILY
    definition_period = YEAR
    label = "Wisconsin WHEAP housing type"
    defined_for = StateCode.WI
    # Section 4.4.13 housing types.
    # PDF pages 76-77
    reference = "https://web.archive.org/web/20260428215048/https://energyandhousing.wi.gov/Documents/WHEAP/WheapManual_PY26.pdf#page=76"
