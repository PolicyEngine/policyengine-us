from policyengine_us.model_api import *


class ga_caps_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Georgia CAPS"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=29",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=30",
        "https://www.decal.ga.gov/documents/attachments/CCDFStatePlan25-27.pdf#page=17",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # Section 6.4.1 (the "in order to apply" rule, p.29) extends the age
        # limit to 17 or younger for a child with "a case plan requiring child
        # care as part of court-ordered supervision"; 6.4.3 (p.30) and CCDF
        # Plan 2.2.1(c) say "court order for supervision" / "under court
        # supervision". We treat the case-plan content as a verification
        # detail and use the single court-supervision input, just as
        # is_disabled stands in for the documented disability. The court
        # route shares the disabled-child ceiling. The developmental-delay
        # route and the 6.4.4 continuation through the end of the eligibility
        # period are not modeled.
        court_supervision = person("is_under_court_supervision", period.this_year)
        age_eligible = where(
            is_disabled | court_supervision,
            age <= p.disabled_child,
            age < p.child,
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
