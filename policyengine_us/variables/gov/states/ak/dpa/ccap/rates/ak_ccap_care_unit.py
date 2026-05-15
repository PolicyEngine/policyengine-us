from policyengine_us.model_api import *


class AKCCAPCareUnit(Enum):
    FT_MONTH = "Full-time month"
    PT_MONTH = "Part-time month"
    FT_DAY = "Full-time day"
    PT_DAY = "Part-time day"


class ak_ccap_care_unit(Variable):
    value_type = Enum
    entity = Person
    possible_values = AKCCAPCareUnit
    default_value = AKCCAPCareUnit.FT_MONTH
    definition_period = MONTH
    label = "Alaska CCAP care unit (provider billing schedule)"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/wsvhl3v3/ccap-rate-schedule.pdf#page=1"
