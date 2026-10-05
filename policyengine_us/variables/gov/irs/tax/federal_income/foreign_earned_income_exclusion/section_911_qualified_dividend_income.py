from policyengine_us.model_api import *


class section_911_qualified_dividend_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified dividends less the section 911 capital gain excess"
    unit = USD
    documentation = (
        "Qualified dividend income for the regular tax rates. A taxpayer with "
        "a section 911 capital gain excess reduces qualified dividends by the "
        "part of the excess that exceeds net capital gain other than "
        "qualified dividends. Equals qualified dividend income for everyone "
        "else."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(2)(A)(ii)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_2_A_ii",
        ),
        dict(
            title="2025 Form 1040 instructions, Foreign Earned Income Tax Worksheet—Line 16, footnote, modification 2",
            href="https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=37",
        ),
    ]

    def formula(tax_unit, period, parameters):
        qualified_dividends = add(tax_unit, period, ["qualified_dividend_income"])
        net_capital_gain = tax_unit("net_capital_gain", period)
        excess = tax_unit("section_911_capital_gain_excess", period)
        # Net capital gain determined without regard to section 1(h)(11).
        gain_other_than_dividends = max_(0, net_capital_gain - qualified_dividends)
        excess_over_other_gain = max_(0, excess - gain_other_than_dividends)
        return where(
            excess > 0,
            max_(0, qualified_dividends - excess_over_other_gain),
            qualified_dividends,
        )
