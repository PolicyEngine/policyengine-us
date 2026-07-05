from policyengine_us.model_api import *


class MICCAPExemptLevel(Enum):
    LEVEL_1 = "Level 1"
    LEVEL_2 = "Level 2"


class mi_ccap_exempt_level(Variable):
    value_type = Enum
    entity = Person
    possible_values = MICCAPExemptLevel
    default_value = MICCAPExemptLevel.LEVEL_1
    definition_period = MONTH
    label = "Michigan CDC license-exempt provider quality level"
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/RF/Public/RFT/270.pdf#page=4"
    )
