from policyengine_us.model_api import *


class section_911_net_capital_gain_other_than_qualified_dividends(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gain other than qualified dividends, less the section 911 capital gain excess"
    unit = USD
    documentation = (
        "Net capital gain determined without regard to section 1(h)(11), for "
        "the regular tax rates. A section 911 capital gain excess reduces it "
        "first, but not below zero. Equals net capital gain less qualified "
        "dividends (not below zero) for everyone else."
    )
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 911(f)(2)(A)(i)",
        href="https://www.law.cornell.edu/uscode/text/26/911#f_2_A_i",
    )

    def formula(tax_unit, period, parameters):
        qualified_dividends = add(tax_unit, period, ["qualified_dividend_income"])
        gain = max_(0, tax_unit("net_capital_gain", period) - qualified_dividends)
        excess = tax_unit("section_911_capital_gain_excess", period)
        return where(excess > 0, max_(0, gain - excess), gain)
