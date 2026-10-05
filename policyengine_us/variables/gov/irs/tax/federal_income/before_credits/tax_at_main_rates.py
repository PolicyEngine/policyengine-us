from policyengine_us.model_api import *


def amounts_in_brackets(taxable_amount, filing_status, bracket):
    """Each bracket's key and the part of an amount that falls in it.

    `bracket` is a bracket parameter node with `rates` and `thresholds`,
    such as `parameters(period).gov.irs.income.bracket` or a contrib
    reform's replacement schedule. A threshold of infinity leaves every
    bracket above it empty.
    """
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
        yield b, max_(0, min_(taxable_amount, bracket_top) - bracket_bottom)
        bracket_bottom = bracket_top


def tax_at_main_rates(taxable_amount, filing_status, bracket):
    """Tax on an amount at the ordinary rate schedule of 26 U.S.C. 1.

    `bracket` is a bracket parameter node, as in `amounts_in_brackets`.
    """
    tax = 0
    for b, amount in amounts_in_brackets(taxable_amount, filing_status, bracket):
        tax += bracket.rates[b] * amount
    return tax


def amount_taxed_below_rate(taxable_amount, filing_status, bracket, rate):
    """The part of an amount that the ordinary rate schedule taxes below a rate.

    For example, 26 U.S.C. 1(h)(1)(A)(ii)(I) refers to "the amount of taxable
    income taxed at a rate below 25 percent". The brackets are those of
    tax_at_main_rates, so the amount is consistent with the tax.
    """
    amount_below_rate = 0
    for b, amount in amounts_in_brackets(taxable_amount, filing_status, bracket):
        if bracket.rates[b] < rate:
            amount_below_rate += amount
    return amount_below_rate
