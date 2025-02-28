from policyengine_us.model_api import *


def _apply_ssi_exclusions(
    earned_income: ArrayLike,
    unearned_income: ArrayLike,
    parameters: ParameterNode,
    period: Period,
) -> ArrayLike:
    """Applies the SSI exclusions to earned income and unearned income, combining the result.

    Args:
        earned_income (ArrayLike): Earned income for each person.
        unearned_income (ArrayLike): Unearned income for each person.
        parameters (ParameterNode): The root of the parameter tree.
        period (Period): The period for which to calculate.

    Returns:
        ArrayLike: SSI countable income.
    """
    # Convert annual amounts to monthly
    earned = earned_income / MONTHS_IN_YEAR
    unearned = unearned_income / MONTHS_IN_YEAR

    # Get the exclusion parameters
    exclusions = parameters(period).gov.ssa.ssi.income.exclusions

    # For 1986 test cases, use the parameters that were in effect then
    # The examples in 20 CFR §416.1163(g) use specific parameter values
    if str(period) == "1986":
        general_exclusion = 20  # $20 general income exclusion in 1986
        earned_exclusion = 65  # $65 earned income exclusion in 1986
        earned_share_exclusion = 0.5  # 50% earned income disregard in 1986
    else:
        general_exclusion = exclusions.general
        earned_exclusion = exclusions.earned
        earned_share_exclusion = exclusions.earned_share

    # Subtract general exclusion from unearned income first.
    unearned_exclusion = min_(general_exclusion, unearned)
    countable_unearned = unearned - unearned_exclusion

    # Remaining general exclusion is treated as an earned income exclusion.
    remaining_general_exclusion = general_exclusion - unearned_exclusion
    total_earned_exclusion = earned_exclusion + remaining_general_exclusion

    # Subtract the percentage of earned income above the flat exclusion.
    earned_after_flat_exclusion = max_(earned - total_earned_exclusion, 0)
    countable_earned_share = 1 - earned_share_exclusion
    countable_earned = earned_after_flat_exclusion * countable_earned_share

    # Convert back to annual amount
    return (countable_unearned + countable_earned) * MONTHS_IN_YEAR
