from policyengine_us.model_api import *


class MTCCAPCareTime(Enum):
    FULL_TIME = "Full-Time"
    HALF_TIME = "Half-Time"


class mt_ccap_care_time(Variable):
    value_type = Enum
    entity = Person
    possible_values = MTCCAPCareTime
    default_value = MTCCAPCareTime.FULL_TIME
    definition_period = MONTH
    defined_for = StateCode.MT
    label = "Montana Best Beginnings Child Care Scholarship care time"
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.205"

    # ARM 37.80.205 sets half-time as 5 or fewer hours of care per day and
    # full-time as more than 5 to 12 hours per day. We don't track per-day care
    # hours at the moment, so this defaults to full-time. Extended care
    # (12-18 hours = 1.25x, over 18 hours = 1.5x) is not modeled.
