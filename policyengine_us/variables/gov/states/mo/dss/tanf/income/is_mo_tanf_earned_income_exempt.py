from policyengine_us.model_api import *


class is_mo_tanf_earned_income_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Person whose earned income is exempt for Missouri TANF"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-120",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-35-10/",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-35-15/",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # 13 CSR 40-2.120(6)(A)1 and DSS Manual 0210.015.35.10 exclude all
        # earned income of a dependent child receiving TA who is a full-time
        # student or a part-time student not employed full-time (approximated
        # here by student status). The six-month calendar-year limitation on
        # this exclusion within the 185% gross income test is not modeled;
        # the exclusion is unlimited in the grant computation.
        in_secondary_school = person("is_in_secondary_school", period.this_year)
        student = person("is_full_time_student", period.this_year) | in_secondary_school
        dependent_child = person("mo_tanf_dependent_child", period)
        student_child = dependent_child & student
        # DSS Manual 0210.015.35.15 also excludes the earnings of a parent
        # under age 19 who is a full-time student in a secondary school or an
        # equivalent level of vocational or technical training.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        caretaker = (
            head_or_spouse & ~is_dependent & person.tax_unit.any(dependent_child)
        )
        age = person("monthly_age", period)
        p = parameters(period).gov.hhs.tanf.cash.eligibility.age_limit
        teen_parent_student = caretaker & (age < p.student) & in_secondary_school
        return student_child | teen_parent_student
