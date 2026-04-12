from policyengine_us.model_api import *


def cap_state_non_refundable_credit(
    tax_unit,
    period,
    credit_name: str,
    ordered_credits,
    income_tax_before_non_refundable_credits_var: str,
    potential,
):
    # Keep raw credit variables as their underlying worksheet/statutory amounts.
    # Ordered tax-liability capping is applied when state non-refundable credits
    # are aggregated into the tax calculation.
    return potential


def ordered_capped_state_non_refundable_credits(
    tax_unit,
    period,
    ordered_credits,
    income_tax_before_non_refundable_credits_var: str,
):
    remaining_tax = tax_unit(income_tax_before_non_refundable_credits_var, period)
    capped_total = 0
    for credit in list(ordered_credits):
        credit_amount = tax_unit(credit, period)
        applied_credit = min_(credit_amount, max_(remaining_tax, 0))
        capped_total += applied_credit
        remaining_tax = max_(remaining_tax - applied_credit, 0)
    return capped_total
