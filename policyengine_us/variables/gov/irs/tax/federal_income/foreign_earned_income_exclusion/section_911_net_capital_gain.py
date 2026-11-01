from policyengine_us.model_api import *


class section_911_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gain less the section 911 capital gain excess"
    unit = USD
    documentation = (
        "Net capital gain, including qualified dividends, for the regular tax "
        "rates. A taxpayer with a section 911 capital gain excess reduces the "
        "gain other than qualified dividends by the excess, then the "
        "qualified dividends by the rest, which leaves net capital gain equal "
        "to taxable income. Equals net capital gain for everyone else."
    )
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 911(f)(2)(A)(i)-(ii)",
        href="https://www.law.cornell.edu/uscode/text/26/911#f_2_A",
    )

    def formula(tax_unit, period, parameters):
        net_capital_gain = tax_unit("net_capital_gain", period)
        excess = tax_unit("section_911_capital_gain_excess", period)
        return where(excess > 0, max_(0, net_capital_gain - excess), net_capital_gain)
