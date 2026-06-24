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
        # Apply person-level age deduction directly (separate VAGI worksheet, Line 14).
        age_deduction = person("va_age_deduction_person", period)
        # Apply the Social Security / Tier 1 Railroad subtraction directly to the
        # person who received the benefits (separate VAGI worksheet, Line 15).
        # Virginia exempts federally taxable Social Security in full, so a spouse
        # whose only income is Social Security has no separate Virginia taxable
        # income. Prorating this subtraction by federal AGI share would instead
        # shift it to a higher-income spouse and wrongly inflate this spouse's
        # VAGI (affecting the Spouse Tax Adjustment).
        social_security_subtraction = person("taxable_social_security", period)
        total_social_security_subtraction = person.tax_unit(
            "tax_unit_taxable_social_security", period
        )
        # Prorate the remaining (non-age, non-Social-Security) subtractions by
        # federal AGI share.
        total_subtractions = person.tax_unit("va_subtractions", period)
        total_age_deduction = person.tax_unit("va_age_deduction", period)
        prorated_subtractions = max_(
            total_subtractions
            - total_age_deduction
            - total_social_security_subtraction,
            0,
        )
        total_federal_agi = person.tax_unit.sum(person_fagi)
        prorate = where(total_federal_agi > 0, person_fagi / total_federal_agi, 0)
        person_prorated_subtractions = prorated_subtractions * prorate
        # Prorate additions the same way
        additions = person.tax_unit("va_additions", period)
        person_additions = additions * prorate
        return (
            person_fagi
            + person_additions
            - age_deduction
            - social_security_subtraction
            - person_prorated_subtractions
        )
