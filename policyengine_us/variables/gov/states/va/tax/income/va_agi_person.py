from policyengine_us.model_api import *


class va_agi_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia adjusted gross income for each person"
    unit = USD
    definition_period = YEAR
    # Virginia includes an individual level definition for AGI
    reference = "https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/13-5"
    defined_for = StateCode.VA

    def formula(person, period, parameters):
        person_fagi = person("adjusted_gross_income_person", period)
        # Apply person-level age deduction directly
        age_deduction = person("va_age_deduction_person", period)
        # Prorate non-age subtractions by federal AGI share
        total_subtractions = person.tax_unit("va_subtractions", period)
        total_age_deduction = person.tax_unit("va_age_deduction", period)
        non_age_subtractions = max_(total_subtractions - total_age_deduction, 0)
        total_federal_agi = person.tax_unit.sum(person_fagi)
        prorate = where(total_federal_agi > 0, person_fagi / total_federal_agi, 0)
        person_non_age_subtractions = non_age_subtractions * prorate
        # Prorate additions the same way
        additions = person.tax_unit("va_additions", period)
        person_additions = additions * prorate
        return (
            person_fagi + person_additions - age_deduction - person_non_age_subtractions
        )
