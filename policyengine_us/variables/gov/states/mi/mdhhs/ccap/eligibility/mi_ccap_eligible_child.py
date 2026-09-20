from policyengine_us.model_api import *


class mi_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Michigan CDC"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=2",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/703.pdf#page=1",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mi.mdhhs.ccap.eligibility
        age = person("age", period.this_year)
        requires_constant_care = person("is_disabled", period.this_year)
        court_supervised = person("is_under_court_supervision", period.this_year)
        court_constant_care = person(
            "mi_ccap_requires_court_ordered_constant_care", period.this_year
        )
        # BEM 703 pp1-2: general supervision extends eligibility below 18.
        # At 18, constant care and both high-school conditions are required.
        high_school_student = person(
            "is_in_secondary_school", period.this_year
        ) & person("is_in_k12_school", period.this_year)
        graduating_student = (
            high_school_student
            & person("is_full_time_student", period.this_year)
            & person("mi_ccap_expected_to_graduate_before_19", period.this_year)
        )
        age_eligible = (
            (age < p.child_age_limit)
            | (
                (requires_constant_care | court_supervised | court_constant_care)
                & (age < p.disabled_child_age_limit)
            )
            | (
                (requires_constant_care | court_constant_care)
                & graduating_student
                & (age < p.student_age_limit)
            )
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        return age_eligible & immigration_eligible & is_dependent
