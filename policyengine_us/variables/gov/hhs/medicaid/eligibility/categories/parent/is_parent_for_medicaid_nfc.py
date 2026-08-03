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
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.categories.parent
        # 42 CFR 435.110 covers parents and other caretaker relatives who
        # live with a dependent child and assume primary responsibility for
        # the child's care (42 CFR 435.4). The tax-unit filer roles proxy
        # the caretaker-relative relationship, so other non-dependent adults
        # in the tax unit do not qualify.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_dependent = person("is_tax_unit_dependent", period)
        # A dependent child is under the age limit, or a full-time student
        # under the student age limit. Foster children are excluded because
        # foster placement is not a relationship by blood, adoption, or
        # marriage.
        age = person("age", period)
        dc = p.dependent_child
        is_student = person("is_full_time_student", period)
        age_qualifies = (age < dc.age_limit) | (
            (age < dc.student_age_limit) & is_student
        )
        in_foster_care = add(person, period, ["is_in_foster_care"]) > 0
        is_dependent_child = is_dependent & age_qualifies & ~in_foster_care
        has_dependent_child_in_tax_unit = person.tax_unit.sum(is_dependent_child) > 0

        # A person claimed as a tax dependent is not the caretaker filer,
        # even if the spouse-inference formula ranks an adult dependent as
        # the tax-unit spouse.
        meets_basic_criteria = (
            is_head_or_spouse & ~is_dependent & has_dependent_child_in_tax_unit
        )

        state = person.household("state_code_str", period)
        requires_deprivation = p.requires_deprivation[state]

        is_single_parent = person("is_single_parent_household", period)
        requires_deprivation_bool = requires_deprivation.astype(bool)
        meets_deprivation = ~requires_deprivation_bool | is_single_parent

        return meets_basic_criteria & meets_deprivation
