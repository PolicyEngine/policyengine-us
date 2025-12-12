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
        # Calculate separate Virginia AGI for each person
        # This follows the VA Form 760 Spouse Tax Adjustment Worksheet
        # which shows "Separate Virginia Adjusted Gross Income" calculation
        # on page 12 of the instructions

        # Start with federal AGI for this person
        federal_agi = person("adjusted_gross_income_person", period)

        # Add Virginia-specific additions for this person
        va_additions = person("va_additions_person", period)

        # Subtract Virginia-specific subtractions for this person
        va_subtractions = person("va_subtractions_person", period)

        # Calculate separate VAGI for this person
        return federal_agi + va_additions - va_subtractions
