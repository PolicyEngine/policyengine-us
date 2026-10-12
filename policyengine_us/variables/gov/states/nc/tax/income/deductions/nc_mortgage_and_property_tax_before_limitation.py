from policyengine_us.model_api import *


class nc_mortgage_and_property_tax_before_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina mortgage interest and real estate property taxes before limitation"
    unit = USD
    definition_period = YEAR
    documentation = "Form D-400 Schedule A line 3: home mortgage interest (line 1) plus real estate property taxes (line 2), before the $20,000 limitation. Calculated for all states so a separately filing spouse outside North Carolina contributes to the shared cap."
    reference = (
        # N.C. Gen. Stat. 105-153.5(a)(2)b
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # 2025 Form D-401 instructions, Form D-400 Schedule A lines 1 to 3
        "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=20",
    )
    # Both spouses' amounts enter the shared cap even if one lives outside NC.
    # Only the final limitation and deduction are restricted to NC returns.

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)

        mortgage_interest = add(tax_unit, period, ["mortgage_interest"])
        pirs = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        property_taxes = min_(
            add(tax_unit, period, ["real_estate_taxes"]),
            pirs.cap[filing_status],
        )
        return mortgage_interest + property_taxes
