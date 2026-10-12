from policyengine_us.model_api import *


class ny_ccap_age_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Age eligible for the New York Child Care Assistance Program"
    defined_for = StateCode.NY
    documentation = (
        "New York's age test, which replaces the flat federal under-13 limit. "
        "18 NYCRR 415.1(b)(2)-(3) extends eligibility to a child with special "
        "needs or under court supervision who is under 18, or under 19 and a "
        "full-time student in a secondary school or equivalent vocational or "
        "technical training. 415.1(c) defines a child with special needs by "
        "conditions requiring special education or related services, for "
        "which is_disabled is the closest available variable. Both routes "
        "read is_in_secondary_school or is_in_k12_school as full-time "
        "secondary or equivalent-training enrollment, as in federal TANF, so "
        "a post-secondary student is not admitted at age 18. The Child Care "
        "Block Grant carry-over in 415.1(b)(2)-(3), which keeps a child "
        "eligible through the end of the eligibility period (up to age 19 or "
        "20), is not modeled."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/415-Child-Care-Services.pdf#page=2",
        "https://otda.ny.gov/policy/directives/1997/ADM/97_ADM-17.pdf#page=4",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.eligibility.age_limit
        age = person("age", period)
        special_needs = person("is_disabled", period)
        under_court_supervision = person("is_under_court_supervision", period)
        # is_in_k12_school is imputed only through age 17, so an 18-year-old
        # still in secondary school is captured via is_in_secondary_school (as
        # in mo_ccs_eligible_child).
        secondary_student = person("is_in_secondary_school", period) | person(
            "is_in_k12_school", period
        )
        extended_age_eligible = (age < p.special_needs) | (
            secondary_student & (age < p.special_needs_student)
        )
        return (age < p.base) | (
            (special_needs | under_court_supervision) & extended_age_eligible
        )
