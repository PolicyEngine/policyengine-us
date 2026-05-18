from policyengine_us.model_api import *


class AKCCAPCareSchedule(Enum):
    FT_MONTH = "Full-time month"
    PT_MONTH = "Part-time month"
    FT_DAY = "Full-time day"
    PT_DAY = "Part-time day"


class ak_ccap_care_schedule(Variable):
    value_type = Enum
    entity = Person
    possible_values = AKCCAPCareSchedule
    default_value = AKCCAPCareSchedule.FT_MONTH
    definition_period = MONTH
    label = "Alaska CCAP care schedule (provider billing)"
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/wsvhl3v3/ccap-rate-schedule.pdf#page=1"
