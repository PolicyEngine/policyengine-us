from policyengine_us.model_api import *


class OKLIHEAPDwellingType(Enum):
    STANDARD = "Standard dwelling"
    ROOMER = "Roomer"


class ok_liheap_dwelling_type(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = OKLIHEAPDwellingType
    default_value = OKLIHEAPDwellingType.STANDARD
    definition_period = YEAR
    label = "Oklahoma LIHEAP dwelling type"
    defined_for = StateCode.OK
    reference = "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-7-a.pdf#page=1"
