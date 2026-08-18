from policyengine_us.model_api import *


class ny_ccap_age_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Age eligible for the New York Child Care Assistance Program"
    defined_for = StateCode.NY
    documentation = (
        "New York's age test, which replaces the flat federal under-13 limit. "
        "18 NYCRR 415.1(b) extends eligibility to a child under 18 with "
        "special needs, and to a full-time secondary student under 19 with "
        "special needs. 415.1(c) defines a child with special needs by "
        "conditions requiring special education or related services, for "
        "which is_disabled is the closest available variable. "
        "is_full_time_student stands in for the full-time secondary or "
        "vocational student of 415.1(b)(3), so a post-secondary student with "
        "special needs is also admitted. The parallel "
        "route for a child under court supervision is not modeled because "
        "PolicyEngine has no variable identifying court supervision."
    )
    reference = "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=2"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.eligibility.age_limit
        age = person("age", period)
        special_needs = person("is_disabled", period)
        student = person("is_full_time_student", period)
        return (
            (age < p.base)
            | (special_needs & (age < p.special_needs))
            | (special_needs & student & (age < p.special_needs_student))
        )
