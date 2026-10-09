from policyengine_us.model_api import *


class nc_wagering_losses_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina wagering losses itemized deduction"
    unit = USD
    documentation = (
        "North Carolina itemized deduction, from 2025, for the wagering losses "
        "allowed under 26 U.S.C. 165(d), to the extent they are not deducted "
        "in arriving at adjusted gross income."
    )
    definition_period = YEAR
    reference = (
        # N.C. Gen. Stat. 105-153.5(a)(2)e
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # S.L. 2026-41, Section 44.2, PDF pages 607-608
        "https://www.ncleg.gov/EnactedLegislation/SessionLaws/PDF/2025-2026/SL2026-41.pdf#page=607",
        # NCDOR FAQs Regarding Recent Session Law Changes, Q36-Q40, PDF pages 11-12
        "https://www.ncdor.gov/faqs-recent-session-law-changes/open#page=11",
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nc.tax.income.deductions.itemized
        # The federal deduction is the amount allowed under section 165(d).
        # PolicyEngine deducts no wagering losses in arriving at AGI.
        return p.wagering_losses.in_effect * tax_unit(
            "wagering_losses_deduction", period
        )
