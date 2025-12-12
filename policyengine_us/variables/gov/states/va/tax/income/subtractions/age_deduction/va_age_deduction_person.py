from policyengine_us.model_api import *


class va_age_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia age deduction for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16"
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.va.tax.income.subtractions.age_deduction

        filing_status = person.tax_unit("filing_status", period)

        age = person("age", period)
        birth_year = period.start.year - age

        agi = person("adjusted_gross_income_person", period)

        # Check if person is eligible for an age deduction
        eligible = age >= p.age_minimum

        # Check if person is eligible for full deduction (no income limit)
        eligible_for_full_deduction = (
            birth_year < p.birth_year_limit_for_full_amount
        )

        # Calculate the maximum allowable deduction amount per person
        maximum_allowable_deduction = p.amount * eligible

        # Calculate the amount that the adjusted federal AGI exceeds the threshold
        excess = max_(agi - p.threshold[filing_status], 0)

        # Reduce by the entire excess, unless eligible for the full deduction
        reduction = excess * where(eligible_for_full_deduction, 0, 1)

        return max_(maximum_allowable_deduction - reduction, 0)
