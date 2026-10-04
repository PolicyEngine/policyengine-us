from policyengine_us.model_api import *


class form_4952_net_investment_gain(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 net investment gain"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 4d: "Net gain from the disposition of property held for
    investment". Its instructions define the "excess, if any, of your total
    gains over your total losses" and include capital gain distributions
    and capital loss carryovers. The model has no split between investment
    and other capital assets, so it treats every capital asset as property
    held for investment, matching the Schedule D Tax Worksheet Form 4952
    helper's arithmetic and aggregation of all tax-unit members.
    long_term_capital_gains already includes Schedule D distributions;
    non_sch_d_capital_gains adds distributions reported without Schedule D.
    There is no capital loss carryover input. Form 4797 business-property
    gains (other_net_gain) are excluded.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_B_ii",
        "https://www.law.cornell.edu/uscode/text/26/163#d_5",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    def formula(tax_unit, period, parameters):
        net_gains = tax_unit("net_capital_gains", period)
        distributions = add(tax_unit, period, ["non_sch_d_capital_gains"])
        return max_(0, net_gains + distributions)
