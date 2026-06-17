from policyengine_us.model_api import *


class MOCCSTimeCategory(Enum):
    FULL_TIME = "Full time"
    HALF_TIME = "Half time"
    PART_TIME = "Part time"


class mo_ccs_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = MOCCSTimeCategory
    default_value = MOCCSTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "Missouri Child Care Subsidy care time unit"
    defined_for = StateCode.MO
    reference = "https://dese.mo.gov/sites/dese/files/media/pdf/2025/10/10.2025%20Income%20Eligibility%20Table%20%282%29.pdf"

    def formula(person, period, parameters):
        # The chart's full/half/part thresholds (5/3/0.5 hours) are per day of
        # care, so the daily-hours input is used, not the weekly total.
        hours = person("childcare_hours_per_day", period.this_year)
        p = parameters(period).gov.states.mo.dese.ccs.time_category
        # The hours bracket returns the MOCCSTimeCategory enum index:
        # 0 = FULL_TIME, 1 = HALF_TIME, 2 = PART_TIME.
        return p.hours.calc(hours)
