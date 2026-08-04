from policyengine_us.model_api import *


class ks_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Kansas CCAP"
    definition_period = MONTH
    defined_for = StateCode.KS
    reference = "https://content.dcf.ks.gov/ees/keesm/Current/keesm2810.htm"

    def formula(person, period, parameters):
        # KEESM 2810: eligible from birth through the eligibility period in which
        # the child turns 13. Children 14-18 qualify only if they are incapable
        # of self-care (modeled via the special-needs branch) or under court
        # supervision. We don't track court supervision or eligibility-period
        # boundaries at the moment, so the 14-18 extension applies only to
        # children with a disability or developmental delay.
        p = parameters(period).gov.states.ks.dcf.ccap.eligibility
        age = person("age", period.this_year)
        has_special_needs = person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
        age_eligible = where(
            has_special_needs,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
