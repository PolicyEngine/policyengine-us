from policyengine_us.model_api import *


class RICCAPTimeCategory(Enum):
    FULL_TIME = "Full Time"
    THREE_QUARTER_TIME = "Three Quarter Time"
    HALF_TIME = "Half Time"
    QUARTER_TIME = "Quarter Time"


class ri_ccap_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = RICCAPTimeCategory
    default_value = RICCAPTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "Rhode Island CCAP time authorization category"
    defined_for = StateCode.RI
    reference = "https://rules.sos.ri.gov/regulations/part/218-20-00-4#4.7.1"

    def formula(person, period, parameters):
        hours = person("childcare_hours_per_week", period.this_year)
        p = parameters(period).gov.states.ri.dhs.ccap.time_authorization
        return p.thresholds.calc(hours)
