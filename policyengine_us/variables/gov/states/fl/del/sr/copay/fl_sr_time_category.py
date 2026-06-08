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
    reference = "https://www.elcduval.org/wp-content/uploads/2025/07/Rule-6M-4.400_Frequently-Asked-Questions.pdf#page=2"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.fl["del"].sr.copay
        hours = person("childcare_hours_per_week", period.this_year)
        return where(
            hours >= p.full_time_hours_threshold,
            FLSRTimeCategory.FULL_TIME,
            FLSRTimeCategory.PART_TIME,
        )
