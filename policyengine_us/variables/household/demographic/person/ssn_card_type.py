from policyengine_us.model_api import *


class SSNCardType(Enum):
    CITIZEN = "Citizen"
    NON_CITIZEN_VALID_EAD = "Non-citizen with valid EAD card"
    OTHER_NON_CITIZEN = "Other non-citizen"
    NONE = "None"


class ssn_card_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = SSNCardType
    default_value = SSNCardType.CITIZEN
    definition_period = YEAR
    label = "Social Security Number (SSN) card type as an enumeration type"
