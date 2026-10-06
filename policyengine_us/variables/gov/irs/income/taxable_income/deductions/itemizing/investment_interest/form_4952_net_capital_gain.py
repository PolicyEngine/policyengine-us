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
    for investment and only the head's and spouse's gains count. Schedule D
    distributions already belong to long_term_capital_gains, so
    distributions reported without Schedule D are added once. Capital loss
    carryovers have no model input and are not modeled.

    This is also Schedule D Tax Worksheet line 4, so the capital gains tax
    takes a Form 4952 line 4g election from the same amount. It does not read
    the worksheet, which reads it.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_B_ii_II",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf#page=3",
        "https://www.irs.gov/pub/irs-prior/i1040sd--2025.pdf#page=15",
    ]

    def formula(tax_unit, period, parameters):
        net_gain = tax_unit("form_4952_net_investment_gain", period)
        long_term_gains = tax_unit_non_dep_add(
            tax_unit, period, ["long_term_capital_gains"]
        ) + tax_unit("form_4952_capital_gain_distributions", period)
        short_term_gains = tax_unit_non_dep_add(
            tax_unit, period, ["short_term_capital_gains"]
        )
        net_capital_gain = max_(0, long_term_gains - max_(0, -short_term_gains))
        return min_(net_gain, net_capital_gain)
