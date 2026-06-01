from policyengine_us.model_api import *


class ga_caps_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Georgia CAPS"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=30",
        "https://www.decal.ga.gov/documents/attachments/CCDFStatePlan25-27.pdf#page=16",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.age_threshold
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # Per Policy Manual §6.4.1, the age 13-17 extension also covers children
        # whose case plan requires child care as part of court-ordered supervision;
        # we don't track court-ordered supervision at the moment, so only the
        # disability pathway is modeled.
        age_eligible = where(is_disabled, age <= p.disabled_child, age < p.child)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
