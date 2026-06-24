from policyengine_us.model_api import *


class cdcc_income_floor_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the CDCC spouse earned income floor"
    definition_period = YEAR
    reference = "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section21&num=0&edition=prelim"

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        has_spouse = person.tax_unit.sum(head_or_spouse) > 1
        student_or_disabled = person("is_full_time_student", period) | person(
            "is_incapable_of_self_care", period
        )
        return head_or_spouse & has_spouse & student_or_disabled
