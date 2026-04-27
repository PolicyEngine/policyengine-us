from policyengine_us.model_api import *


class medicaid_non_filer_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child-age eligible for Medicaid MAGI non-filer household rules"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_3_iv"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.household
        age = person("age", period.this_year)
        student = person("is_full_time_student", period.this_year)
        return (age < p.child_age_limit.non_student) | (
            p.uses_full_time_student_under_21_rule & student & (age < 21)
        )
