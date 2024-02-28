from policyengine_us.model_api import *


class retirement_saving_eligible_person(Variable):
    entity = Person
    definition_period = YEAR
    label = "retirement_saving_contributions_credit_eligible_person"
    value_type = bool
    reference = "https://www.irs.gov/pub/irs-pdf/f8880.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving
        age_eligible = person("age", period) >= p.age
        not_full_time_student = person("is_full_time_student", period) == False
        not_claimed_on_another_return = (
            person("claimed_as_dependent_on_another_return", period) == False
        )
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        is_head_or_spouse = head | spouse
        return (
            age_eligible
            * is_head_or_spouse
            * not_full_time_student
            * not_claimed_on_another_return
        )
