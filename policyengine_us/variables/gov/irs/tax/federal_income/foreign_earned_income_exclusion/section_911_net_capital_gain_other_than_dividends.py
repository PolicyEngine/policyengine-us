from policyengine_us.model_api import *


def section_911_net_capital_gain_other_than_dividends(tax_unit, period):
    """Net capital gain determined without regard to section 1(h)(11), for the
    regular tax rates: reduced first, but not below zero, by any section 911
    capital gain excess (26 U.S.C. 911(f)(2)(A)(i)).

    Computed in place rather than stored as a variable: a stored amount is
    rounded to single precision, which moved capital_gains_tax by fractions
    of a cent for filers with nothing excluded.
    """
    # Schedule D Tax Worksheet line 6: the qualified dividends net_capital_gain
    # still holds after any Form 4952 line 4g election, bounded by any direct
    # net_capital_gain input.
    net_capital_gain = tax_unit("net_capital_gain", period)
    qualified_dividends = min_(
        max_(0, tax_unit("dividend_income_reduced_by_investment_income", period)),
        net_capital_gain,
    )
    gain = max_(0, net_capital_gain - qualified_dividends)
    excess = tax_unit("section_911_capital_gain_excess", period)
    return where(excess > 0, max_(0, gain - excess), gain)
