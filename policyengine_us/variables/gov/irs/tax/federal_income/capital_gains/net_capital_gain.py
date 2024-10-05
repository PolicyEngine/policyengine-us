from policyengine_us.model_api import *


class net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Net capital gain"
    unit = USD
    documentation = (
        "The excess of net long-term capital gain over net short-term capital"
        'loss, plus qualified dividends (the definition of "net capital gain"'
        "which applies to 26 U.S.C. § 1(h) from § 1(h)(11))."
    )
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1222(11)",
        href="https://www.law.cornell.edu/uscode/text/26/1222#11",
    )

    def formula(tax_unit, period, parameters):
        lt_capital_gain = max_(
            0, add(tax_unit, period, ["long_term_capital_gains"])
        )
        st_capital_loss = max_(
            0, -add(tax_unit, period, ["short_term_capital_gains"])
        )
        net_cap_gain = max_(0, lt_capital_gain - st_capital_loss)
        qual_div_income = add(tax_unit, period, ["qualified_dividend_income"])
        return net_cap_gain + qual_div_income
