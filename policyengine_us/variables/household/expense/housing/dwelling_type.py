from policyengine_us.model_api import *


class DwellingType(Enum):
    HOUSE = "House, including modular homes"
    DUPLEX = "Duplex"
    APARTMENT = "Apartment"
    MOBILE_HOME = "Mobile home"
    TRAILER = "Trailer"
    OTHER = "Other dwelling"
    UNSPECIFIED = "Unspecified"


class dwelling_type(Variable):
    value_type = Enum
    entity = Household
    possible_values = DwellingType
    default_value = DwellingType.UNSPECIFIED
    definition_period = YEAR
    label = "Dwelling type"
    reference = "https://data.census.gov/table/ACSDT1Y2024.B25024"
