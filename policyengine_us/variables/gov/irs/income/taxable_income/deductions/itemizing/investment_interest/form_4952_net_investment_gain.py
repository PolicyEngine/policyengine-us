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
    held for investment. Only the head's and spouse's gains count: a tax unit
    dependent's gains belong on the dependent's own return, as in
    irs_gross_income. long_term_capital_gains already includes Schedule D
    distributions; non_sch_d_capital_gains adds distributions reported
    without Schedule D, floored at zero for each filer as in irs_gross_income.
    The long_term_capital_loss_carryover input is a memo amount whose loss
    is already included in long_term_capital_gains; it is not subtracted again. Form 4797 business-property
    gains (other_net_gain) are excluded.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_4_B_ii",
        "https://www.law.cornell.edu/uscode/text/26/163#d_5",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf#page=3",
    ]

    def formula(tax_unit, period, parameters):
        gains = tax_unit_non_dep_add(
            tax_unit, period, ["long_term_capital_gains", "short_term_capital_gains"]
        )
        distributions = tax_unit("form_4952_capital_gain_distributions", period)
        return max_(0, gains + distributions)
