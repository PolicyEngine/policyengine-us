from policyengine_us.model_api import *


class sc_tanf_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "South Carolina TANF dependent child"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        # PDF pages 105, 132, 134
        "https://dss.sc.gov/media/bxwc1jdj/tanf-policy-manual-volume-67-final.pdf#page=105",
    )
    documentation = (
        "A member who meets the dependent-child age test, under 18 or under "
        "19 in secondary school, and doesn't head the household. The tax "
        "unit's head or spouse heads it, and in a group with no adult the "
        "oldest member does, and members who tie for oldest all do, so a "
        "minor parent who heads the household counts as a parent."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.tanf.cash.eligibility.age_limit
        year = period.this_year
        age = person("age", year)
        # Unlike is_person_demographic_tanf_eligible, pregnancy does not make
        # an adult a dependent child, so her wages stay counted.
        in_secondary_school = person("is_in_secondary_school", year)
        age_limit = where(in_secondary_school, p.student, p.non_student)
        meets_age_test = age < age_limit
        # Section 7.5 counts a minor parent's earned income "if the minor
        # parent is the head-of-household" and excludes it when the minor
        # parent is a dependent in the benefit group. The tax unit head or
        # spouse stands in for the head of household.
        head_or_spouse = person("is_tax_unit_head_or_spouse", year)
        # Tax-unit roles are inferred only for adults, so a minor parent who
        # lives with no adult heads no tax unit unless roles are input. The
        # oldest member of a group with no adult heads the household; members
        # who tie for oldest all head it, so the result doesn't depend on the
        # order in which members are listed.
        no_adult = ~person.spm_unit.any(~person("is_child", year))
        oldest = age == person.spm_unit.max(age)
        heads_household = head_or_spouse | (no_adult & oldest)
        return meets_age_test & ~heads_household
