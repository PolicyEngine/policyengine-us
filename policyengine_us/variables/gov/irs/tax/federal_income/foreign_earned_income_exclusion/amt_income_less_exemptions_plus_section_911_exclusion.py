from policyengine_us.model_api import *


class amt_income_less_exemptions_plus_section_911_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "AMT taxable excess plus the section 911 exclusion"
    unit = USD
    documentation = (
        "The AMT taxable excess (alternative minimum taxable income less the "
        "exemption) increased by the foreign earned income and housing amounts "
        "excluded under 26 U.S.C. 911(a), when there is a taxable excess. The "
        "tentative minimum tax of a taxpayer excluding foreign earned income "
        "is the tax on this amount less the tax on the excluded amount alone. "
        "Line 3 of the Form 6251 Foreign Earned Income Tax Worksheet; equals "
        "the taxable excess for everyone else."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(1)(B)(i)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_1_B_i",
        ),
        dict(
            title="2025 Form 6251 instructions, Foreign Earned Income Tax Worksheet—Line 7, line 3",
            href="https://www.irs.gov/pub/irs-pdf/i6251.pdf#page=10",
        ),
    ]

    def formula(tax_unit, period, parameters):
        taxable_excess = tax_unit("amt_income_less_exemptions", period)
        excluded = max_(0, tax_unit("foreign_earned_income_exclusion", period))
        # Section 911(f)(1)(B) applies only if there is a taxable excess; the
        # worksheet is skipped when Form 6251 line 6 is zero.
        return taxable_excess + where(taxable_excess > 0, excluded, 0)
