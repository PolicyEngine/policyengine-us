from policyengine_us.model_api import *


class ky_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Kentucky CCAP"
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = "https://apps.legislature.ky.gov/law/kar/downloads/docs/10239/document.engrossed.pdf#page=4"

    def formula(person, period, parameters):
        # 922 KAR 2:160 Section 3(1)(b): under 13, or under 19 if incapable
        # of self-care or under court supervision. Federal-priority status,
        # immunization verification, and provider-relationship restrictions
        # remain unmodeled.
        p = parameters(period).gov.states.ky.dcbs.ccap.eligibility
        age = person("age", period.this_year)
        has_special_need = person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
        under_court_supervision = person("is_under_court_supervision", period.this_year)
        age_eligible = where(
            has_special_need | under_court_supervision,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        # Section 3(1)(a)2: child must be a U.S. citizen or qualified alien.
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
