from policyengine_us.model_api import *


class KSLIEAPDwellingType(Enum):
    HOUSE_MODULAR_MOBILE = "House, modular home or mobile home"
    DUPLEX = "Duplex"
    APARTMENT = "Apartment"
    TRAILER_OTHER = "Trailer or other dwelling"


class ks_liheap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = KSLIEAPDwellingType
    default_value = KSLIEAPDwellingType.HOUSE_MODULAR_MOBILE
    definition_period = YEAR
    label = "Kansas LIEAP dwelling type"
    documentation = "Dwelling type column of the Kansas LIEAP benefit matrix: house, modular home or mobile home; duplex; apartment; or trailer or other dwelling. Defaults to the house, modular or mobile home column."
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/KS_BenefitMatrix_2026.pdf#page=1"
