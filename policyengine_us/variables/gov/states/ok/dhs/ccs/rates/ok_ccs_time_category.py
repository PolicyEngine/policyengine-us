from policyengine_us.model_api import *


class OKCCSTimeCategory(Enum):
    FULL_TIME = "Full time"
    PART_TIME = "Part time"


class ok_ccs_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = OKCCSTimeCategory
    default_value = OKCCSTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "Oklahoma Child Care Subsidy daily unit type"
    defined_for = StateCode.OK
    reference = "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-4-b.pdf#page=1"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.ccs.time_category
        # The full-time daily unit type is approved when the child needs care
        # more than four hours per day; the part-time daily unit type when the
        # child needs four or fewer hours per day (Appendix C-4-B). Zero hours
        # means the input is unset, so it falls back to full time per the
        # declared default rather than being treated as part time.
        hours = person("childcare_hours_per_day", period.this_year)
        is_part_time = (hours > 0) & (hours <= p.max_part_time_hours)
        return where(
            is_part_time,
            OKCCSTimeCategory.PART_TIME,
            OKCCSTimeCategory.FULL_TIME,
        )
