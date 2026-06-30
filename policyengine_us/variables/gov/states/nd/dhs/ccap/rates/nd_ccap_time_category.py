from policyengine_us.model_api import *


class NDCCAPTimeCategory(Enum):
    FULL_TIME = "Full time"
    PART_TIME = "Part time"


class nd_ccap_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = NDCCAPTimeCategory
    default_value = NDCCAPTimeCategory.PART_TIME
    definition_period = MONTH
    label = "North Dakota CCAP level of care"
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.time_category
        # Full-time level of care is 25 or more hours per week; part-time is
        # 1 to fewer than 25 hours per week (400-28-80-50).
        hours = person("childcare_hours_per_week", period.this_year)
        return where(
            hours >= p.full_time_min_hours,
            NDCCAPTimeCategory.FULL_TIME,
            NDCCAPTimeCategory.PART_TIME,
        )
