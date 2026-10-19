from policyengine_us.model_api import *


class nc_mortgage_and_property_tax_before_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina mortgage interest and real estate property taxes before limitation"
    unit = USD
    definition_period = YEAR
    documentation = "Form D-400 Schedule A line 3: home mortgage interest (line 1) plus real estate property taxes (line 2), before the $20,000 limitation. Line 1 is the interest allowed under section 163(h) of the Code, after the federal acquisition-debt limits. Calculated for all states so a separately filing spouse outside North Carolina contributes to the shared cap."
    reference = (
        # SL 2026-31 section 12(a) adopts the IRC as of July 5, 2025,
        # including the permanent $750,000 acquisition-debt limit from 2026.
        "https://www.ncleg.gov/EnactedLegislation/SessionLaws/PDF/2025-2026/SL2026-31.pdf#page=42",
        # N.C. Gen. Stat. 105-153.5(a)(2)b
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # 2025 Form D-401 instructions, Form D-400 Schedule A lines 1 to 3
        "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=20",
    )
    # Both spouses' amounts enter the shared cap even if one lives outside NC.
    # Only the final limitation and deduction are restricted to NC returns.

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)

        # Line 1 is "the amount allowed as a deduction for interest ... under
        # section 163(h) of the Code", so interest on acquisition debt above
        # the federal limits is excluded.
        mortgage_interest = add(tax_unit, period, ["deductible_mortgage_interest"])
        pirs = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            pirs.cap[filing_status],
        )
        return mortgage_interest + property_taxes
