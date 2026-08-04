from policyengine_us.model_api import *


class ky_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Kentucky CCAP"
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/services/karmaservice/documents/10239/ToPDF?markup=false#page=4"

    def formula(person, period, parameters):
        # 922 KAR 2:160 Section 3(1)(b): a child must be under 13, or under 19 if
        # physically/mentally incapable of self-care, under court supervision, or a
        # federal-priority child. We don't track court-supervision or
        # federal-priority status at the moment, so the 13-18 extension applies
        # only via the special-need branch (is_disabled / has_developmental_delay).
        # We also don't track the immunization-certificate requirement
        # (Section 3(1)(c)) or provider-relationship restrictions (Section 3(3)) at
        # the moment.
        p = parameters(period).gov.states.ky.dcbs.ccap.eligibility
        age = person("age", period.this_year)
        has_special_need = person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
        age_eligible = where(
            has_special_need,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        # Section 3(1)(a)2: child must be a U.S. citizen or qualified alien.
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
