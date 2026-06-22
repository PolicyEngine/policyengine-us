from policyengine_us.model_api import *


class oh_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Ohio CCAP"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = ("https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-01",)

    def formula(person, period, parameters):
        # 5180:2-16-01(V): publicly funded child care covers children under
        # age 13. 5180:2-16-01(AA),(W): a special-needs child (chronic health
        # condition or developmental delay) qualifies up to age 18. We use
        # has_developmental_delay as the special-needs proxy.
        p = parameters(period).gov.states.oh.dcy.ccap.eligibility
        age = person("age", period.this_year)
        has_developmental_delay = person("has_developmental_delay", period.this_year)
        age_eligible = where(
            has_developmental_delay,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        # 5180:2-16-01 Appendix B / 45 CFR 98.20: only the child in need of
        # care must meet citizenship or qualified-noncitizen status; the
        # parent's immigration status is not tested.
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
