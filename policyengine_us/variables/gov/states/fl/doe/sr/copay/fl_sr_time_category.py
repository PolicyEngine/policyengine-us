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
    reference = "https://www.flrules.org/gateway/RuleNo.asp?id=6M-4.500"

    def formula(person, period, parameters):
        # Per 6M-4.500(1)(b),(1)(j) the full-time vs part-time "unit of care" is
        # defined by each coalition's rate schedule, not a statewide hours cutoff;
        # the threshold parameter is a modeling stand-in (see its YAML comment).
        p = parameters(period).gov.states.fl.doe.sr.copay
        hours = person("childcare_hours_per_week", period.this_year)
        return where(
            hours >= p.full_time_hours_threshold,
            FLSRTimeCategory.FULL_TIME,
            FLSRTimeCategory.PART_TIME,
        )
