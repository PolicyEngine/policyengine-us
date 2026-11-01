from policyengine_us.model_api import *


def section_911_net_capital_gain_other_than_dividends(tax_unit, period):
    """Net capital gain determined without regard to section 1(h)(11), for the
    regular tax rates: reduced first, but not below zero, by any section 911
    capital gain excess (26 U.S.C. 911(f)(2)(A)(i)).

    Computed in place rather than stored as a variable: a stored amount is
    rounded to single precision, which moved capital_gains_tax by fractions
    of a cent for filers with nothing excluded.
    """
    # The head and spouse's qualified dividends, as in net_capital_gain.
    qualified_dividends = tax_unit_non_dep_add(
        tax_unit, period, ["qualified_dividend_income"]
    )
    gain = max_(0, tax_unit("net_capital_gain", period) - qualified_dividends)
    excess = tax_unit("section_911_capital_gain_excess", period)
    return where(excess > 0, max_(0, gain - excess), gain)
