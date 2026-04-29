from policyengine_us.model_api import *


class NJCCAPTimeCategory(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"


class nj_ccap_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = NJCCAPTimeCategory
    default_value = NJCCAPTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "New Jersey CCAP time authorization category"
    defined_for = StateCode.NJ
    reference = "https://www.childcarenj.gov/ChildCareNJ/media/media_library/Max_CC_Payment_Rates.pdf#page=1"

    def formula(person, period, parameters):
        hours = person("childcare_hours_per_week", period.this_year)
        p = parameters(period).gov.states.nj.njdhs.ccap.time_authorization
        return p.thresholds.calc(hours)
