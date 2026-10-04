from policyengine_us.model_api import *


class form_4952_net_capital_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 net capital gain"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 4e: "Enter the smaller of line 4d or your net capital gain
    from the disposition of property held for investment." The instructions
    define net capital gain as the "excess, if any, of your net long-term
    capital gain over your net short-term capital loss" and state "Capital
    gain distributions from mutual funds are treated as long-term capital
    gains." As on line 4d, every capital asset is treated as property held
    for investment and all tax-unit members' gains are summed, matching the
    Schedule D Tax Worksheet Form 4952 helper. Schedule D distributions
    already belong to long_term_capital_gains; add non_sch_d_capital_gains
    once. Capital loss carryovers have no model input and are not modeled.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_B_ii_II",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    def formula(tax_unit, period, parameters):
        net_gain = tax_unit("form_4952_net_investment_gain", period)
        long_term_gains = add(tax_unit, period, ["long_term_capital_gains"])
        short_term_gains = add(tax_unit, period, ["short_term_capital_gains"])
        distributions = add(tax_unit, period, ["non_sch_d_capital_gains"])
        net_capital_gain = max_(
            0, long_term_gains + distributions - max_(0, -short_term_gains)
        )
        return min_(net_gain, net_capital_gain)
