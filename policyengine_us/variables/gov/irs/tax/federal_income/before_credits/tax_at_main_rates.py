from policyengine_us.model_api import *


def tax_at_main_rates(taxable_amount, filing_status, bracket):
    """Tax on an amount at the ordinary rate schedule of 26 U.S.C. 1.

    `bracket` is a bracket parameter node with `rates` and `thresholds`,
    such as `parameters(period).gov.irs.income.bracket` or a contrib
    reform's replacement schedule.
    """
    tax = 0
    bracket_bottom = 0
    for i in range(1, len(list(bracket.rates.__iter__())) + 1):
        b = str(i)
        # Clamp to the running lower bound: with a non-monotone threshold
        # configuration, amount_between's clip returns the upper bound for
        # every input, so an inverted bracket would add
        # rate * (top - bottom) < 0 to every filer of the status at any
        # income (#9084).
        bracket_top = max_(bracket_bottom, bracket.thresholds[b][filing_status])
        tax += bracket.rates[b] * amount_between(
            taxable_amount, bracket_bottom, bracket_top
        )
        bracket_bottom = bracket_top
    return tax


def amount_taxed_below_rate(taxable_amount, filing_status, bracket, rate):
    """The part of an amount that the ordinary rate schedule taxes below a rate.

    For example, 26 U.S.C. 1(h)(1)(A)(ii)(I) refers to "the amount of taxable
    income taxed at a rate below 25 percent". Brackets are walked and clamped
    as in tax_at_main_rates, so the amount is consistent with the tax.
    """
    amount = 0
    bracket_bottom = 0
    for i in range(1, len(list(bracket.rates.__iter__())) + 1):
        b = str(i)
        bracket_top = max_(bracket_bottom, bracket.thresholds[b][filing_status])
        if bracket.rates[b] < rate:
            amount += amount_between(taxable_amount, bracket_bottom, bracket_top)
        bracket_bottom = bracket_top
    return amount
