from policyengine_us.model_api import *


class nh_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for New Hampshire Child Care Scholarship Program"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.07"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ccap.eligibility
        age = person("monthly_age", period)
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.disabled_child_age_limit, p.child_age_limit)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "nh_ccap_immigration_status_eligible_person", period
        )
        return age_eligible & is_dependent & immigration_eligible
