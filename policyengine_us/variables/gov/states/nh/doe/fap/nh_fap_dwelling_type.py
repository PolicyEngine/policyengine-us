from policyengine_us.model_api import *


class NHFAPDwellingType(Enum):
    MOBILE_HOME = "Mobile home"
    APARTMENT_CONDO_OR_DUPLEX = "Apartment, condominium or duplex"
    SINGLE_FAMILY_OR_MODULAR = "Single family or modular home"


class nh_fap_dwelling_type(Variable):
    value_type = Enum
    possible_values = NHFAPDwellingType
    default_value = NHFAPDwellingType.SINGLE_FAMILY_OR_MODULAR
    entity = SPMUnit
    definition_period = YEAR
    label = "New Hampshire FAP dwelling type"
    reference = "https://www.energy.nh.gov/sites/g/files/ehbemt551/files/inline-documents/sonh/fuel-assistance-program-procedures-manual.pdf#page=77"
    # The single-family/modular default is a modeling assumption. Private
    # rented rooms require room-use details absent from the bedroom proxy.
