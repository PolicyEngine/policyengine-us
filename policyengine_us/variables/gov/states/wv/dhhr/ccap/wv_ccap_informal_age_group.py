from policyengine_us.model_api import *


class WVCCAPInformalAgeGroup(Enum):
    UNDER_2 = "Under 2 years"
    AGE_2_AND_OVER = "2 years and over"


class wv_ccap_informal_age_group(Variable):
    value_type = Enum
    entity = Person
    possible_values = WVCCAPInformalAgeGroup
    default_value = WVCCAPInformalAgeGroup.AGE_2_AND_OVER
    definition_period = MONTH
    label = "West Virginia CCAP informal care age group"
    defined_for = StateCode.WV
    reference = "https://bfa.wv.gov/media/6831/download?inline#page=1"

    def formula(person, period, parameters):
        age_in_months = person("age", period.this_year) * MONTHS_IN_YEAR
        p = parameters(period).gov.states.wv.dhhr.ccap.age_group
        return p.informal_months.calc(age_in_months)
