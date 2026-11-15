from policyengine_us.model_api import *


def _apply_ssi_exclusions_monthly(
    earned_income: ArrayLike,
    unearned_income: ArrayLike,
    parameters: ParameterNode,
    period: Period,
    general_exclusion: ArrayLike = None,
) -> ArrayLike:
    """
    Applies standard SSI income exclusions to one month's earned and unearned
    income, returning that month's countable income. This follows
    20 CFR §§ 416.1112 and 416.1124:
      1) Subtract $20 'general' exclusion from unearned (or from earned if unearned < 20).
      2) Subtract $65 'earned' exclusion from any remaining earned income.
      3) Exclude 50% of the remainder of earned income.
    """
    p = parameters(period).gov.ssa.ssi.income.exclusions
    general_exclusion = p.general if general_exclusion is None else general_exclusion

    # Step 1: Subtract general exclusion from unearned first
    applied_general = min_(general_exclusion, unearned_income)
    countable_unearned = unearned_income - applied_general

    # The remainder of the general exclusion (if unearned < 20) applies to earned
    leftover_general = general_exclusion - applied_general
    total_earned_excl = p.earned + leftover_general

    # Step 2 & 3: Apply the total earned exclusion, then exclude 50% of the rest
    earned_after_flat = max_(earned_income - total_earned_excl, 0)
    # The 'earned_share' parameter is the fraction excluded above the flat. Typically 0.5 => 50% excluded.
    # So the fraction that remains is (1 - earned_share).
    countable_earned = earned_after_flat * (1.0 - p.earned_share)

    return countable_unearned + countable_earned


def _apply_ssi_exclusions(
    earned_income: ArrayLike,
    unearned_income: ArrayLike,
    parameters: ParameterNode,
    period: Period,
    general_exclusion: ArrayLike = None,
) -> ArrayLike:
    """
    Applies the standard SSI income exclusions to annual earned and unearned
    income, treating each month as one-twelfth of the year, and returns
    annual countable income. The exclusions are monthly amounts, so this
    converts annual -> monthly, applies them, then goes back to annual.
    """
    monthly = _apply_ssi_exclusions_monthly(
        earned_income / MONTHS_IN_YEAR,
        unearned_income / MONTHS_IN_YEAR,
        parameters,
        period,
        general_exclusion,
    )
    return monthly * MONTHS_IN_YEAR
