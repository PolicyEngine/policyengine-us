from policyengine_us.model_api import *


class INCCDFPTQLevel(Enum):
    BASE = "Unrated"
    PTQ_1 = "Paths to QUALITY Level 1"
    PTQ_2 = "Paths to QUALITY Level 2"
    PTQ_3 = "Paths to QUALITY Level 3"
    PTQ_4 = "Paths to QUALITY Level 4"


class in_ccdf_ptq_level(Variable):
    value_type = Enum
    entity = Person
    possible_values = INCCDFPTQLevel
    default_value = INCCDFPTQLevel.BASE
    definition_period = MONTH
    defined_for = StateCode.IN
    label = "Indiana CCDF Paths to QUALITY level"
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=37"
    )
