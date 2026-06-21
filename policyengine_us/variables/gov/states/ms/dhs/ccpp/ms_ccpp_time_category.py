from policyengine_us.model_api import *


class MSCCPPTimeCategory(Enum):
    PART_TIME = "Part time"
    FULL_TIME = "Full time"


class ms_ccpp_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = MSCCPPTimeCategory
    default_value = MSCCPPTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "Mississippi CCPP care time category"
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=12"

    def formula(person, period, parameters):
        hours_per_day = person("childcare_hours_per_day", period.this_year)
        p = parameters(period).gov.states.ms.dhs.ccpp.time_category
        # Part-time = care for fewer than 6 hours of a 24-hour day; full-time is
        # 6 or more hours. The bracket returns 0=PART_TIME, 1=FULL_TIME, which
        # PolicyEngine maps to the enum index.
        return p.hours.calc(hours_per_day)
