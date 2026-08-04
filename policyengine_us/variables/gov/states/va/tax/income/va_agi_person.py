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
        # Virginia's "Worksheet for Determining Separate Virginia Adjusted Gross
        # Income" (Form 760 instructions) attributes each subtraction to the
        # spouse who received the underlying income (va_subtractions_person),
        # then sets each spouse's separate VAGI. This matters for the Spouse Tax
        # Adjustment: a spouse whose only income is Virginia-exempt (e.g. Social
        # Security, railroad retirement, unemployment) has no separate Virginia
        # taxable income, so the couple should not qualify for the adjustment.
        person_subtractions = person("va_subtractions_person", period)
        # Additions are only defined at the tax-unit level, so prorate them by
        # federal AGI share.
        additions = person.tax_unit("va_additions", period)
        total_federal_agi = person.tax_unit.sum(person_fagi)
        prorate = where(total_federal_agi > 0, person_fagi / total_federal_agi, 0)
        person_additions = additions * prorate
        return person_fagi + person_additions - person_subtractions
