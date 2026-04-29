"""Shared helpers for ordered state nonrefundable credits.

These helpers distinguish between:

- potential credit amounts: the worksheet or statutory amount before applying
  overall nonrefundable ordering and tax-liability limits
- applied credit amounts: the amount actually allowed on the return after
  accounting for earlier credits and remaining liability

Downstream formulas should only read applied credit variables when the form or
statute refers to the post-ordering amount that lands on the return. If a
downstream formula refers to the underlying worksheet amount, it should read
the corresponding ``*_potential`` variable instead.
"""

from policyengine_us.model_api import *


def state_non_refundable_credit_limit(
    tax_unit,
    period,
    ordered_credits,
    income_tax_before_non_refundable_credits_var: str,
    credit_name: str,
):
    """Return the remaining liability available to ``credit_name``.

    Only credits that appear earlier in ``ordered_credits`` reduce the amount
    available to this credit. Later credits must not affect this limit.
    """
    preceding_credits = []
    for credit in list(ordered_credits):
        if credit == credit_name:
            break
        preceding_credits.append(credit)

    income_tax_before_credits = tax_unit(
        income_tax_before_non_refundable_credits_var, period
    )
    preceding_credit_total = (
        add(tax_unit, period, preceding_credits) if preceding_credits else 0
    )
    return max_(income_tax_before_credits - preceding_credit_total, 0)


def applied_state_non_refundable_credit(
    tax_unit,
    period,
    ordered_credits,
    income_tax_before_non_refundable_credits_var: str,
    credit_name: str,
    potential_credit_name: str,
):
    """Cap a potential state credit to the liability remaining at its turn."""
    potential = tax_unit(potential_credit_name, period)
    credit_limit = state_non_refundable_credit_limit(
        tax_unit,
        period,
        ordered_credits,
        income_tax_before_non_refundable_credits_var,
        credit_name,
    )
    return min_(potential, credit_limit)


def cap_state_non_refundable_credit(
    tax_unit,
    period,
    credit_name: str,
    ordered_credits,
    income_tax_before_non_refundable_credits_var: str,
    potential,
):
    """Preserve the pre-ordering credit amount on the raw credit variable.

    This helper exists for compatibility with older variable formulas that used
    a generic "cap" helper. The raw credit variable should still represent the
    underlying worksheet/statutory amount; the ordered application happens only
    when nonrefundable credits are aggregated into tax.
    """
    return potential


def ordered_capped_state_non_refundable_credits(
    tax_unit,
    period,
    ordered_credits,
    income_tax_before_non_refundable_credits_var: str,
):
    """Apply ordered nonrefundable credits without exceeding tax liability."""
    remaining_tax = tax_unit(income_tax_before_non_refundable_credits_var, period)
    capped_total = 0
    for credit in list(ordered_credits):
        credit_amount = tax_unit(credit, period)
        applied_credit = min_(credit_amount, max_(remaining_tax, 0))
        capped_total += applied_credit
        remaining_tax = max_(remaining_tax - applied_credit, 0)
    return capped_total
