from policyengine_us.model_api import *


class OHCCAPTimeCategory(Enum):
    HOURLY = "Hourly"
    PART_TIME = "Part-time"
    FULL_TIME = "Full-time"


class oh_ccap_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = OHCCAPTimeCategory
    default_value = OHCCAPTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "Ohio CCAP child care time category"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:6-1-10"

    def formula(person, period, parameters):
        # 5180:6-1-10(H): Hourly under 10 hours/week, Part-time 10 to under
        # 33 hours/week, Full-time 33 or more hours/week. The bracket returns
        # the enum index (0=Hourly, 1=Part-time, 2=Full-time).
        hours = person("childcare_hours_per_week", period.this_year)
        p = parameters(period).gov.states.oh.dcy.ccap.time_category
        return p.hours.calc(hours)
