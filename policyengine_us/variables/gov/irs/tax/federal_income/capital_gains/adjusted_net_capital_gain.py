from policyengine_us.model_api import *


class adjusted_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted net capital gain"
    unit = USD
    documentation = "The excess of net long-term capital gain over net short-term capital loss."
    definition_period = YEAR
    reference = dict(
        title="26 U.S. Code § 1(h)(3)",
        href="https://www.law.cornell.edu/uscode/text/26/1#h_3",
    )

    def formula(tax_unit, period, parameters):
        net_capital_gain = tax_unit("net_capital_gain", period)
        # The law actually uses the original definition of 'net capital gain' which does not include
        # qualified dividend income, but separately adds qualified dividends here. The definition of
        # 'net capital gain' in the variable 'net_capital_gain' actually has some very specific exclusion
        # criteria for particular types of dividends and companies, so it's not an *exact* fit to the
        # definition here, but it's a good enough approximation. See 26 U.S. Code § 1(h)(11)(B) for the
        # definition of 'net capital gain' for the above variable, and 26 U.S. Code § 1(h)(3) for the definition
        # of adjusted net capital gain (this variable).
        qualified_dividend_income = add(
            tax_unit, period, ["qualified_dividend_income"]
        )
        unrecaptured_s_1250_gain = tax_unit(
            "unrecaptured_section_1250_gain", period
        )
        cg_28_pct_rate_gain = tax_unit(
            "capital_gains_28_percent_rate_gain", period
        )
        net_gains_less_dividends = max_(
            0,
            net_capital_gain - qualified_dividend_income,
        )
        reduced_capital_gains = max_(
            net_gains_less_dividends
            - (unrecaptured_s_1250_gain + cg_28_pct_rate_gain),
            0,
        )
        return reduced_capital_gains + qualified_dividend_income
