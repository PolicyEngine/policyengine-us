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
        # child is indistinguishable from a caretaker relative.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_dependent = person("is_tax_unit_dependent", period)
        # A dependent child is under the state's age limit (the 42 CFR
        # 435.4 under-18 floor; Georgia and Kansas operate under-19 rules)
        # or, in states electing the 42 CFR 435.4 student option per their
        # state plan S25 page or manual, an 18-year-old full-time student
        # under the student age limit. The is_full_time_student proxy is
        # broader than the regulation's "full-time student in a secondary
        # school (or ... vocational or technical training)" - it also
        # captures full-time college students. It is not gated on
        # is_in_secondary_school because nothing populates that input (no
        # formula, no dataset mapping), so the gate would deny the option
        # in any household that does not set an input most users never
        # see; at age 18 only college enrollment carries microdata
        # signal, so even this proxy fires on the wrong group there -
        # both resolve once the dataset maps CPS secondary enrollment.
        age = person("age", period)
        dc = p.dependent_child
        is_student = person("is_full_time_student", period)
        elects_student_option = dc.student_option[state].astype(bool)
        age_qualifies = (age < dc.age_limit[state]) | (
            elects_student_option & is_student & (age < dc.student_age_limit)
        )
        # Foster children are excluded as a proxy: an unrelated foster
        # parent may claim the child as a tax dependent yet is not a
        # relative by blood, adoption, or marriage. This also excludes
        # kinship foster caregivers, whose blood relationship legally
        # survives the foster placement - a known limitation, since the
        # model cannot distinguish the two placements.
        in_foster_care = add(person, period, ["is_in_foster_care"]) > 0
        is_dependent_child = is_dependent & age_qualifies & ~in_foster_care
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
