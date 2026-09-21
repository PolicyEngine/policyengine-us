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
        "special needs is also admitted by the existing special-needs proxy. "
        "The court-supervision route uses is_in_secondary_school or the "
        "is_in_k12_school imputation to require secondary education or "
        "equivalent training for the under-19 extension."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=2",
        "https://otda.ny.gov/policy/directives/1997/ADM/97_ADM-17.pdf#page=4",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.eligibility.age_limit
        age = person("age", period)
        special_needs = person("is_disabled", period)
        student = person("is_full_time_student", period)
        court_supervision = person("is_under_court_supervision", period)
        # 18 NYCRR 415.1(b)(3): a full-time secondary (or equivalent training)
        # student under court supervision stays eligible until 19. is_in_k12_school
        # is imputed only through age 17, so an 18-year-old still in secondary
        # school is captured via is_in_secondary_school (as in mo_ccs_eligible_child).
        secondary_student = person("is_in_secondary_school", period) | person(
            "is_in_k12_school", period
        )
        court_age_eligible = court_supervision & (
            (age < p.special_needs)
            | (secondary_student & (age < p.special_needs_student))
        )
        return (
            (age < p.base)
            | court_age_eligible
            | (special_needs & (age < p.special_needs))
            | (special_needs & student & (age < p.special_needs_student))
        )
