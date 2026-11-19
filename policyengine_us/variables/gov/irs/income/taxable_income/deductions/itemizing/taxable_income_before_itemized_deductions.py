from policyengine_us.model_api import *


class taxable_income_before_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income before itemized deductions"
    unit = USD
    documentation = (
        "Adjusted gross income less personal exemptions and the deductions an "
        "itemizer takes besides itemized deductions: those 26 U.S.C. 63(b) "
        "allows whether or not the filer itemizes, which 63(d) keeps out of "
        "itemized deductions. This is the taxable income of section 68(a)(2), "
        "determined without regard to section 68 and increased by the "
        "itemized deductions. It is not floored at zero."
    )
    definition_period = YEAR
    reference = (
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section63&num=0&edition=prelim",
        "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section68&num=0&edition=prelim",
        # P.L. 119-21, sec. 70111(a), rewrote section 68 from 2026.
        "https://www.govinfo.gov/content/pkg/PLAW-119publ21/html/PLAW-119publ21.htm",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        agi = tax_unit("adjusted_gross_income", period)
        exemptions = tax_unit("exemptions", period)
        # Section 68(a)(2) adds the itemized deductions back to taxable
        # income, so neither they nor wagering losses (a section 165(d)
        # itemized deduction, listed apart from the other itemized
        # deductions) reduce this amount. Everything else an itemizer
        # deducts does: the section 199A, 224 and 225 deductions, the
        # section 151(d)(5)(C) senior deduction and qualified passenger
        # vehicle loan interest.
        itemized = ["itemized_taxable_income_deductions", "wagering_losses_deduction"]
        other_deductions = [
            deduction
            for deduction in p.deductions_if_itemizing
            if deduction not in itemized
        ]
        return agi - exemptions - add(tax_unit, period, other_deductions)
