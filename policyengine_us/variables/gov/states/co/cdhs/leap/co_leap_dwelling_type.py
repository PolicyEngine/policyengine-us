from policyengine_us.model_api import *


class COLEAPDwellingType(Enum):
    MOBILE_HOME = "Mobile home"
    DUPLEX_TRIPLEX_FOURPLEX = "Duplex, triplex or fourplex"
    TOWNHOUSE = "Townhouse"
    APARTMENT_CONDO = "Apartment or condominium"
    HOTEL_MOTEL = "Hotel or motel"
    CABIN = "Cabin"
    TINY_HOME = "Tiny home"
    CAMPER_RV = "Camper, fifth wheel or recreational vehicle"
    HOUSE_MODULAR = "House or modular home"


class co_leap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = COLEAPDwellingType
    default_value = COLEAPDwellingType.HOUSE_MODULAR
    definition_period = YEAR
    label = "Colorado LEAP dwelling type"
    defined_for = StateCode.CO
    # House/modular is the modeling fallback when dwelling type is unknown.
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/CO_BenefitMatrix_Heat-Crisis_2026.pdf#page=6"
