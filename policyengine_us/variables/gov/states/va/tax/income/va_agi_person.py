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
        total_agi = person.tax_unit("va_agi", period)
        person_agi = person("adjusted_gross_income_person", period)
        total_federal_agi = person.tax_unit.sum(person_agi)

        prorate = np.zeros_like(total_agi)
        mask = total_federal_agi > 0
        prorate[mask] = person_agi[mask] / total_federal_agi[mask]
        return total_agi * prorate
