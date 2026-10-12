from policyengine_us.model_api import *


class in_supplemental_homestead_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana supplemental homestead credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://iga.in.gov/pdf-documents/124/2025/senate/bills/SB0001/SB0001.05.ENRH.pdf#page=124",
        "https://www.in.gov/dlgf/files/2025-memos/250612-Cockerill-Memo-Legislation-Affecting-Deductions%2C-Exemptions%2C-and-Credits.pdf#page=9",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        # Senate Enrolled Act 1 (2025) adds IC 6-1.1-20.6-7.7, a supplemental
        # homestead credit equal to the lesser of 10% of the homestead property
        # tax liability or $300, for taxes first due and payable in 2026 and
        # after. No age or income limit; homeowners only, so renters (with no
        # real estate taxes) receive zero.
        # Modeling approximations, all bounded by the $300 cap: eligibility is
        # proxied by real_estate_taxes > 0 rather than the IC 6-1.1-12-37
        # homestead standard deduction qualification; the base is total
        # real_estate_taxes rather than the homestead-only liability (PE has no
        # homestead-specific variable); and subsection (d)'s exclusion of
        # referendum-approved taxes from the base is not modeled.
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.property.supplemental_homestead_credit
        )
        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        return min_(p.rate * property_tax, p.cap)
