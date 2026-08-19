from policyengine_us.model_api import *


class ILCCAPBaseDayType(Enum):
    FULL_DAY = "Full day"
    PART_DAY = "Part day"


class il_ccap_base_day_type(Variable):
    value_type = Enum
    entity = Person
    possible_values = ILCCAPBaseDayType
    default_value = ILCCAPBaseDayType.FULL_DAY
    definition_period = MONTH
    label = "Illinois CCAP base day type"
    defined_for = StateCode.IL
    reference = "https://idec.illinois.gov/content/dam/soi/en/web/idec/documents/pages/ccap-for-providers/IL444-4343%20-%20Child%20Care%20Payment%20Rates%20for%20Child%20Care%20Providers%207.1.26.pdf#page=1"
