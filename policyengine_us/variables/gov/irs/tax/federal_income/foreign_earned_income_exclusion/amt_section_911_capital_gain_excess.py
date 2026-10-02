from policyengine_us.model_api import *


class amt_section_911_capital_gain_excess(Variable):
    value_type = float
    entity = TaxUnit
    label = "AMT section 911 capital gain excess"
    unit = USD
    documentation = (
        "For a taxpayer excluding foreign earned income under 26 U.S.C. "
        "911(a), the excess of net capital gain over the AMT taxable excess "
        "(Form 6251 line 6). The capital gains used in Form 6251 Part III are "
        "reduced by this excess."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(2)(B)(i)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_2_B_i",
        ),
        dict(
            title="2025 Form 6251 instructions, Part III, Form 2555",
            href="https://www.irs.gov/pub/irs-pdf/i6251.pdf#page=13",
        ),
    ]

    def formula(tax_unit, period, parameters):
        excludes_income = tax_unit("foreign_earned_income_exclusion", period) > 0
        net_capital_gain = tax_unit("net_capital_gain", period)
        taxable_excess = tax_unit("amt_income_less_exemptions", period)
        return where(excludes_income, max_(0, net_capital_gain - taxable_excess), 0)
