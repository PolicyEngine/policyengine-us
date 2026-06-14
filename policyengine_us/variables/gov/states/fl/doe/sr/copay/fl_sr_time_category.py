from policyengine_us.model_api import *


class FLSRTimeCategory(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"


class fl_sr_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = FLSRTimeCategory
    default_value = FLSRTimeCategory.PART_TIME
    definition_period = MONTH
    label = "Florida School Readiness authorized care time category"
    defined_for = StateCode.FL
    reference = "https://www.flsenate.gov/Laws/Statutes/2025/1002.81"

    def formula(person, period, parameters):
        # Fla. Stat. 1002.81(9): full-time care is "at least 6 hours ... within a
        # 24-hour period"; 1002.81(11): part-time care is less than 6 hours within
        # a 24-hour period. This is a DAILY measure, not weekly -- e.g. 4 days x
        # 6 hours is full-time even though it is only 24 hours/week.
        p = parameters(period).gov.states.fl.doe.sr.copay
        hours = person("childcare_hours_per_day", period.this_year)
        return where(
            hours >= p.full_time_hours_threshold,
            FLSRTimeCategory.FULL_TIME,
            FLSRTimeCategory.PART_TIME,
        )
