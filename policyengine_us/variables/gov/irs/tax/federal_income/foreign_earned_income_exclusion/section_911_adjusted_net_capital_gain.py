from policyengine_us.model_api import *


class section_911_adjusted_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted net capital gain less the section 911 capital gain excess"
    unit = USD
    documentation = (
        "Adjusted net capital gain for the regular tax rates, figured from net "
        "capital gain, qualified dividends, unrecaptured section 1250 gain and "
        "28-percent rate gain as each is reduced by a section 911 capital gain "
        "excess. Equals adjusted net capital gain for everyone else."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(2)(A)(iii)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_2_A_iii",
        ),
        dict(
            title="26 U.S. Code § 1(h)(3)",
            href="https://www.law.cornell.edu/uscode/text/26/1#h_3",
        ),
    ]

    def formula(tax_unit, period, parameters):
        excess = tax_unit("section_911_capital_gain_excess", period)
        gain_other_than_dividends = tax_unit(
            "section_911_net_capital_gain_other_than_qualified_dividends", period
        )
        qualified_dividends = tax_unit("section_911_qualified_dividend_income", period)
        unrecaptured_gain = tax_unit(
            "section_911_unrecaptured_section_1250_gain", period
        )
        rate_gain = tax_unit("section_911_28_percent_rate_gain", period)
        # As in adjusted_net_capital_gain: net capital gain determined without
        # regard to section 1(h)(11), reduced (not below zero) by unrecaptured
        # section 1250 gain and 28-percent rate gain, plus qualified dividends.
        # With an excess it is figured from these parts, so an
        # adjusted_net_capital_gain input is not used.
        reduced_gain = max_(
            gain_other_than_dividends - (unrecaptured_gain + rate_gain), 0
        )
        return where(
            excess > 0,
            reduced_gain + qualified_dividends,
            tax_unit("adjusted_net_capital_gain", period),
        )
