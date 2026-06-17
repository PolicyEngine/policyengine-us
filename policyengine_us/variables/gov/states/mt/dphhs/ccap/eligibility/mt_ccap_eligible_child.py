from policyengine_us.model_api import *


class mt_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Montana Best Beginnings Child Care Scholarship"
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.80.201",
        "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/CC21Eligibility070718.pdf#page=4",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ccap.eligibility
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(
            is_disabled, p.special_needs_child_age_limit, p.child_age_limit
        )
        age_eligible = age < age_limit
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
