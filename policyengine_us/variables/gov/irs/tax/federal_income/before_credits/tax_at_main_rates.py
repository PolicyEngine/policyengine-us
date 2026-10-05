from policyengine_us.model_api import *


def tax_at_main_rates(taxable_amount, filing_status, bracket):
    """Tax on an amount at the ordinary rate schedule of 26 U.S.C. 1.

    `bracket` is a bracket parameter node with `rates` and `thresholds`,
    such as `parameters(period).gov.irs.income.bracket` or a contrib
    reform's replacement schedule. A threshold of infinity leaves every
    bracket above it empty, so those brackets add nothing.
    """
    tax = 0
    bracket_bottom = 0
    for i in range(1, len(list(bracket.rates.__iter__())) + 1):
        b = str(i)
        # Clamp to the running lower bound so brackets never overlap: with
        # a non-monotone threshold configuration, an inverted bracket is
        # empty and the next one starts at the highest threshold so far
        # (#9084).
        bracket_top = max_(bracket_bottom, bracket.thresholds[b][filing_status])
        # max(0, min(x, top) - bottom), the form policyengine-core's
        # MarginalRateTaxScale.calc uses, equals amount_between's
        # clip(x, bottom, top) - bottom whenever the bottom is finite. A
        # bracket above an infinite threshold, such as the
        # additional_tax_bracket reform's unset bracket 8, runs from infinity
        # to infinity: there the clip form is inf - inf = NaN, and this form
        # is zero.
        amount_in_bracket = max_(0, min_(taxable_amount, bracket_top) - bracket_bottom)
        tax += bracket.rates[b] * amount_in_bracket
        bracket_bottom = bracket_top
    return tax
