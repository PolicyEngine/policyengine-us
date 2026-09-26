from policyengine_us.model_api import *


class mi_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Michigan CDC"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=1",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.ccap.eligibility
        age = person("age", period.this_year)
        # BEM 703 pp.1-2: a child under 13 is eligible; a child 13 to under 18
        # is eligible if they require constant care due to a physical, mental
        # or psychological condition (is_disabled proxy) or "supervision has
        # been ordered by the court"; an 18-year-old is eligible if they
        # require constant care due to such a condition "or a court order" and
        # are a full-time high school student reasonably expected to complete
        # high school before 19. We use the single court-supervision input
        # for both court conditions, treating the constant-care content of
        # the order as a verification detail; the model may therefore
        # overstate eligibility for a supervised child whose order does not
        # require constant care.
        requires_constant_care = person("is_disabled", period.this_year)
        court_supervision = person("is_under_court_supervision", period.this_year)
        extended_status = requires_constant_care | court_supervision
        # is_in_k12_school is imputed only through age 17, so an 18-year-old
        # still in high school is captured via is_in_secondary_school (as in
        # mo_ccs_eligible_child). is_full_time_student derives from the same
        # imputation, so secondary-school enrollment also satisfies the
        # full-time test (as in is_mo_tanf_earned_income_exempt). Enrollment
        # proxies the expectation of finishing before 19, so the model may
        # overstate eligibility for an enrolled 18-year-old who will not.
        in_secondary_school = person("is_in_secondary_school", period.this_year)
        high_school_student = in_secondary_school | person(
            "is_in_k12_school", period.this_year
        )
        full_time_student = in_secondary_school | person(
            "is_full_time_student", period.this_year
        )
        graduating_student = high_school_student & full_time_student
        age_eligible = (
            (age < p.child_age_limit)
            | (extended_status & (age < p.disabled_child_age_limit))
            | (extended_status & graduating_student & (age < p.student_age_limit))
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & immigration_eligible & is_dependent
