from policyengine_us.model_api import *


class CTC4KCareLevel(Enum):
    FULL_TIME_PLUS = "Full-Time Plus (51-65 hrs/wk)"
    FULL_TIME = "Full-Time (35-50 hrs/wk)"
    HALF_TIME = "Half-Time (16-34 hrs/wk)"
    QUARTER_TIME = "Quarter-Time (1-15 hrs/wk)"


class ct_c4k_care_level(Variable):
    value_type = Enum
    entity = Person
    possible_values = CTC4KCareLevel
    default_value = CTC4KCareLevel.FULL_TIME
    definition_period = MONTH
    defined_for = StateCode.CT
    label = "Connecticut Care 4 Kids care level"
    reference = "https://www.ctoec.org/care-4-kids/c4k-providers/c4k-rates/"

    def formula(person, period, parameters):
        hours = person("childcare_hours_per_week", period.this_year)
        p = parameters(period).gov.states.ct.oec.c4k.care_level
        return p.calc(hours)
