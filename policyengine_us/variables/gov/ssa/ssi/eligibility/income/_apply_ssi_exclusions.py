from policyengine_us.model_api import *


def _apply_ssi_exclusions(
    earned_income: ArrayLike,
    unearned_income: ArrayLike,
    parameters: ParameterNode,
    period: Period,
) -> ArrayLike:
    """
    Applies standard SSI income exclusions to convert total earned/unearned income
    into countable income. This follows 20 CFR §§ 416.1112 and 416.1124:
      1) Subtract $20 'general' exclusion from unearned (or from earned if unearned < 20).
      2) Subtract $65 'earned' exclusion from any remaining earned income.
      3) Exclude 50% of the remainder of earned income.

    All amounts are stored as annual but exclusions are monthly amounts, so we convert
    from annual -> monthly, apply monthly exclusions, then go back to annual.
    """
    # Convert from annual to monthly
    earned_monthly = earned_income / MONTHS_IN_YEAR
    unearned_monthly = unearned_income / MONTHS_IN_YEAR

    p = parameters(period).gov.ssa.ssi.income.exclusions

    # Step 1: Subtract general exclusion from unearned first
    applied_general = min_(p.general, unearned_monthly)
    countable_unearned = unearned_monthly - applied_general

    # The remainder of the general exclusion (if unearned < 20) applies to earned
    leftover_general = p.general - applied_general
    total_earned_excl = p.earned + leftover_general

    # Step 2 & 3: Apply the total earned exclusion, then exclude 50% of the rest
    earned_after_flat = max_(earned_monthly - total_earned_excl, 0)
    # The 'earned_share' parameter is the fraction excluded above the flat. Typically 0.5 => 50% excluded.
    # So the fraction that remains is (1 - earned_share).
    countable_earned = earned_after_flat * (1.0 - p.earned_share)

    # Convert back to annual
    return (countable_unearned + countable_earned) * MONTHS_IN_YEAR
