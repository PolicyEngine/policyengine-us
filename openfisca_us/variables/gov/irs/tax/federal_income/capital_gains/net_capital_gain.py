from openfisca_us.model_api import *


class net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gain"
    unit = USD
    documentation = 'The excess of net long-term capital gain over net short-term capital loss, plus qualified dividends (the definition of "net capital gain" which applies to 26 U.S.C. § 1(h) from § 1(h)(11)).'
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(11)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#11",
    )

    def formula(tax_unit, period, parameters):
        net_long_term_capital_gain = tax_unit(
            "net_long_term_capital_gain", period
        )
        net_short_term_capital_loss = tax_unit(
            "net_short_term_capital_loss", period
        )
        net_capital_gains = max_(
            0, net_long_term_capital_gain - net_short_term_capital_loss
        )
        qualified_dividends = add(
            tax_unit, period, ["qualified_dividend_income"]
        )
        return net_capital_gains + qualified_dividends
