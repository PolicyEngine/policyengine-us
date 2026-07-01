from policyengine_us.model_api import *


class ks_tanf_child_earned_income_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Kansas TANF child whose earned income is exempt"
    definition_period = MONTH
    reference = "https://content.dcf.ks.gov/ees/keesm/current/keesm6410.htm"
    defined_for = StateCode.KS

    def formula(person, period, parameters):
        # Per KEESM 6410: a child's earned income is exempt as income in the
        # month received for a child under age 18, or under age 19 if working
        # toward a high school diploma or its equivalent. This matches the
        # federal TANF minor-child definition (45 CFR 260.30), so we reuse the
        # federal student and non-student age limits.
        age = person("age", period.this_year)
        is_student = person("is_in_secondary_school", period.this_year)
        p = parameters(period).gov.hhs.tanf.cash.eligibility.age_limit
        age_limit = where(is_student, p.student, p.non_student)
        return age < age_limit
