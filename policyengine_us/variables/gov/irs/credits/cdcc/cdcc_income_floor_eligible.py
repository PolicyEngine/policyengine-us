from policyengine_us.model_api import *


class cdcc_income_floor_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the CDCC spouse earned income floor"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#d_2"

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        married = person.tax_unit("tax_unit_married", period)
        student_or_disabled = person("is_full_time_student", period) | person(
            "is_incapable_of_self_care", period
        )
        return head_or_spouse & married & student_or_disabled
