from policyengine_us.model_api import *


class savers_credit_eligible_person(Variable):
    entity = Person
    definition_period = YEAR
    label = "Eligible person for the retirement saving contributions credit"
    value_type = bool
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8880.pdf",
        "https://www.law.cornell.edu/uscode/text/26/25B#c",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.credits.retirement_saving
        age = person("age", period)
        age_eligible = age >= p.age_threshold
        full_time_student = person("is_full_time_student", period)
        claimed_on_another_return = person(
            "claimed_as_dependent_on_another_return", period
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return (
            age_eligible
            & head_or_spouse
            & ~full_time_student
            & ~claimed_on_another_return
        )
