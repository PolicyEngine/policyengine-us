from policyengine_us.model_api import *


class is_parent_for_medicaid_nfc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid parent non-financial criteria"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.110",
        "https://www.law.cornell.edu/cfr/text/42/435.4",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1810-000-00/1810-020-00/1810-020-20/1810-020-20-10/",
        "https://dssmanuals.mo.gov/family-mo-healthnet-magi/1805-000-00/1805-030-00/1805-030-10/1805-030-10-25/",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        state = person.household("state_code_str", period)
        # 42 CFR 435.110 covers parents and other caretaker relatives who
        # live with a dependent child and assume primary responsibility for
        # the child's care. Tax-unit filer roles proxy that relationship:
        # 42 CFR 435.4 names claiming the child as a tax dependent as an
        # indicator of primary responsibility, though the caretaker "is not
        # required to" claim the child (also Missouri DSS § 1805.030.10.25).
        # The model assigns tax-unit dependency from living arrangements
        # rather than actual filing, so non-filer caretakers are captured;
        # kinship itself is not encoded, so an unrelated filer who claims a
        # child is indistinguishable from a caretaker relative. That matches
        # the definition in states electing the 42 CFR 435.4 paragraph (3)
        # option to include any adult who lives with the child and assumes
        # primary responsibility for the child's care.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_dependent = person("is_tax_unit_dependent", period)
        # A dependent child is under the state's age limit (the 42 CFR
        # 435.4 under-18 floor; Georgia and Kansas operate under-19 rules)
        # or, in states electing the 42 CFR 435.4 student option per their
        # state plan S25 page or manual, an 18-year-old "full-time student
        # in a secondary school (or equivalent vocational or technical
        # training)" under the student age limit; college enrollment does
        # not qualify. As in sc_tanf_dependent_child and
        # mo_tanf_dependent_child, is_in_secondary_school marks the
        # student, with attendance standing in for full-time enrollment.
        # A full-time student who is not in college also counts, so
        # callers who set the generic is_full_time_student (or
        # is_in_k12_school) still reach the option. Enrollment under the
        # age limit stands in for the expectation of finishing before 19.
        age = person("age", period)
        dc = p.dependent_child
        in_secondary_school = person("is_in_secondary_school", period)
        is_full_time_student = person("is_full_time_student", period)
        is_college_student = person("is_full_time_college_student", period)
        attends_secondary_school = in_secondary_school | (
            is_full_time_student & ~is_college_student
        )
        elects_student_option = dc.student_option[state].astype(bool)
        age_qualifies = (age < dc.age_limit[state]) | (
            elects_student_option
            & attends_secondary_school
            & (age < dc.student_age_limit)
        )
        # The caretaker relationship, including the treatment of foster
        # children, is shared with the adult group's child coverage
        # requirement.
        in_care = person("is_child_of_medicaid_caretaker", period)
        is_dependent_child = in_care & age_qualifies
        has_dependent_child_in_tax_unit = person.tax_unit.sum(is_dependent_child) > 0

        # A person claimed as a tax dependent is not the caretaker filer,
        # even if the spouse-inference formula ranks an adult dependent as
        # the tax-unit spouse.
        meets_basic_criteria = (
            is_head_or_spouse & ~is_dependent & has_dependent_child_in_tax_unit
        )

        requires_deprivation = p.requires_deprivation[state]

        is_single_parent = person("is_single_parent_household", period)
        requires_deprivation_bool = requires_deprivation.astype(bool)
        meets_deprivation = ~requires_deprivation_bool | is_single_parent

        return meets_basic_criteria & meets_deprivation
