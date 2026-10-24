from policyengine_us.model_api import *


class in_supplemental_homestead_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana supplemental homestead credit"
    unit = USD
    definition_period = YEAR
    reference = (
        # IC 6-1.1-20.6-7.7, added by SEA 1 (2025), SECTION 74
        "https://iga.in.gov/pdf-documents/124/2025/senate/bills/SB0001/SB0001.05.ENRH.pdf#page=124",
        "https://www.in.gov/dlgf/files/2025-memos/250612-Cockerill-Memo-Legislation-Affecting-Deductions%2C-Exemptions%2C-and-Credits.pdf#page=9",
        # DLGF June 18, 2025 FAQ, questions 26-30 and 33, PDF pages 7-9
        "https://www.in.gov/dlgf/files/2025-presentations/250618-FAQ-Webinar-Legislative-Update.pdf#page=7",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        # IC 6-1.1-20.6-7.7 applies to property taxes first due and payable
        # in 2026 and after. Subsection (b) limits the credit to a person who
        # qualifies for the homestead standard deduction under IC 6-1.1-12-37
        # (or the surviving spouse of one who did), against the liability on
        # that same homestead. Subsection (c) sets the credit at the lesser
        # of 10% of that liability or $300, and subsection (d) leaves out
        # taxes approved by referendum or local public question. Generic
        # real_estate_taxes neither establish qualification nor measure the
        # homestead liability, so all three are inputs.
        p = (
            parameters(period)
            .gov.states["in"]
            .tax.property.supplemental_homestead_credit
        )
        eligible = tax_unit("in_supplemental_homestead_credit_eligible", period)
        liability = tax_unit("in_homestead_property_tax_liability", period)
        referendum_tax = tax_unit("in_homestead_referendum_property_tax", period)
        base = max_(liability - referendum_tax, 0)
        return eligible * min_(p.rate * base, p.cap)
