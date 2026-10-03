from policyengine_us.model_api import *


class section_911_capital_gain_excess(Variable):
    value_type = float
    entity = TaxUnit
    label = "Section 911 capital gain excess"
    unit = USD
    documentation = (
        "For a taxpayer excluding foreign earned income under 26 U.S.C. "
        "911(a), the excess of net capital gain over taxable income, "
        "determined without regard to section 911(f). In figuring the tax on "
        "taxable income plus the excluded amount, the capital gains are "
        "reduced by this excess, so that the excluded amount is never taxed "
        "at the capital gains rates. The section 1(h) formulas use this "
        "amount; the Schedule D Tax Worksheet lines (dwks14, dwks19, "
        "regular_tax_before_credits) measure the excess from worksheet line "
        "10, as the worksheet does, which can differ when an investment "
        "income election or capital gain distributions are entered."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(2)(A)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_2_A",
        ),
        dict(
            title="2025 Form 1040 instructions, Foreign Earned Income Tax Worksheet—Line 16, footnote",
            href="https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=37",
        ),
    ]

    def formula(tax_unit, period, parameters):
        excludes_income = tax_unit("foreign_earned_income_exclusion", period) > 0
        net_capital_gain = tax_unit("net_capital_gain", period)
        taxable_income = tax_unit("taxable_income", period)
        return where(excludes_income, max_(0, net_capital_gain - taxable_income), 0)
