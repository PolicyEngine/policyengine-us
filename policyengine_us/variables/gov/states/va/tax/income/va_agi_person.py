from policyengine_us.model_api import *


class va_agi_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia adjusted gross income for each person"
    unit = USD
    documentation = (
        "Each spouse's separate Virginia AGI on a joint Virginia return, as "
        "the Spouse Tax Adjustment uses it: their part of the joint return's "
        "federal AGI (adjusted_gross_income_person), plus their share of the "
        "additions, less the subtractions allocated to them "
        "(va_subtractions_person). Spouses who filed a joint "
        "federal return can instead file separate Virginia returns (filing "
        "status 3), each computing federal AGI as though they had filed "
        "separately on their federal return. PolicyEngine uses the federal "
        "filing status for Virginia, so it does not model that case. After a "
        "separate federal return, federal AGI is that return's own AGI."
    )
    definition_period = YEAR
    reference = (
        # Virginia includes an individual level definition for AGI.
        "https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/13-5",
        # Worksheet for Determining Separate Virginia Adjusted Gross Income.
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2025-760-instructions.pdf#page=18",
        # Filing Status 3: "Compute your federal adjusted gross income as
        # though you had filed separately on your federal return".
        "https://www.tax.virginia.gov/filing-status",
    )
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
        # federal AGI share. A spouse with negative federal AGI gets no share,
        # so neither share is negative or more than the whole.
        additions = person.tax_unit("va_additions", period)
        positive_fagi = max_(person_fagi, 0)
        total_federal_agi = person.tax_unit.sum(positive_fagi)
        prorate = where(
            total_federal_agi > 0,
            np.divide(
                positive_fagi,
                total_federal_agi,
                out=np.zeros_like(total_federal_agi, dtype=float),
                where=total_federal_agi > 0,
            ),
            0,
        )
        person_additions = additions * prorate
        return person_fagi + person_additions - person_subtractions
