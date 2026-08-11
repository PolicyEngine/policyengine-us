from policyengine_us.model_api import *


class mo_tanf_dependent_child(Variable):
    value_type = bool
    entity = Person
    label = "Missouri TANF dependent child"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-325",
        "https://revisor.mo.gov/main/OneSection.aspx?section=208.040",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # Per 13 CSR 40-2.325(1)(A) and RSMo 208.040.1(1), a dependent child
        # is under age 18, or under age 19 and a full-time student in a
        # secondary school (or an equivalent level of vocational or technical
        # training). This matches the federal minor-child definition in
        # 45 CFR 260.30, so we reuse the federal age limits. Full-time
        # enrollment is approximated by secondary-school attendance.
        age = person("monthly_age", period)
        student = person("is_in_secondary_school", period.this_year)
        p = parameters(period).gov.hhs.tanf.cash.eligibility.age_limit
        age_eligible = age < where(student, p.student, p.non_student)
        # Count under-18s regardless of the tax-dependent flag so that
        # child-only units (e.g., where the caretaker is an excluded SSI
        # recipient) still qualify; the flag only distinguishes an
        # 18-year-old student child from an 18-year-old caretaker.
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        under_18 = person("is_child", period.this_year)
        return age_eligible & (is_dependent | under_18)
