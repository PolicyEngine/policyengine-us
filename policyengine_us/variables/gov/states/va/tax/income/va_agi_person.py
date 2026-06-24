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
        # spouse who received the underlying income, then sets each spouse's
        # separate VAGI. Apply the subtractions we can resolve at the person
        # level directly to the recipient, and prorate only the remainder.
        #
        # Attributing these per person matters for the Spouse Tax Adjustment: a
        # spouse whose only income is Virginia-exempt (Social Security, railroad
        # retirement, or unemployment) has no separate Virginia taxable income.
        # Prorating these subtractions by federal AGI share would instead shift
        # them onto a higher-income spouse and wrongly inflate this spouse's VAGI.
        age_deduction = person("va_age_deduction_person", period)  # Line 14
        person_subtractions = (
            person("taxable_social_security", period)  # Line 15 (Social Security)
            + person("railroad_benefits", period)  # Line 15 (Tier 1 Railroad)
            + person("unemployment_compensation", period)  # Line 17
        )
        directly_attributed = age_deduction + person_subtractions
        total_directly_attributed = person.tax_unit.sum(directly_attributed)
        # The remaining subtractions are only available at the tax-unit level
        # (e.g. US government interest, the military and disability subtractions,
        # the 529 deduction), so they are still prorated by federal AGI share.
        total_subtractions = person.tax_unit("va_subtractions", period)
        prorated_subtractions = max_(total_subtractions - total_directly_attributed, 0)
        total_federal_agi = person.tax_unit.sum(person_fagi)
        prorate = where(total_federal_agi > 0, person_fagi / total_federal_agi, 0)
        person_prorated_subtractions = prorated_subtractions * prorate
        # Prorate additions the same way
        additions = person.tax_unit("va_additions", period)
        person_additions = additions * prorate
        return (
            person_fagi
            + person_additions
            - directly_attributed
            - person_prorated_subtractions
        )
