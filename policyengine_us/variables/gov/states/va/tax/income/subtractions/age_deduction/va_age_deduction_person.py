from policyengine_us.model_api import *


class va_age_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia age deduction allocated to each person"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16"
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.age_deduction

        total_deduction = person.tax_unit("va_age_deduction", period)

        age = person("age", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible = is_head_or_spouse & (age >= p.age_minimum)

        count_eligible = person.tax_unit.sum(eligible)
        safe_count = max_(count_eligible, 1)
        return where(
            eligible,
            total_deduction / safe_count,
            0,
        )
