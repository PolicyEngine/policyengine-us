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

    Returns:
        ArrayLike: SSI countable income.
    """

    earned = earned_income / MONTHS_IN_YEAR
    unearned = unearned_income / MONTHS_IN_YEAR
    exclusions = parameters(period).gov.ssa.ssi.income.exclusions
    # Subtract general exclusion from unearned income first.
    unearned_exclusion = min_(exclusions.general, unearned)
    countable_unearned = unearned - unearned_exclusion
    # Remaining general exclusion is treated as an earned income exclusion.
    remaining_general_exclusion = exclusions.general - unearned_exclusion
    earned_exclusion = exclusions.earned + remaining_general_exclusion
    # Subtract the percentage of earned income above the flat exclusion.
    earned_after_flat_exclusion = max_(earned - earned_exclusion, 0)
    countable_earned_share = 1 - exclusions.earned_share
    countable_earned = earned_after_flat_exclusion * countable_earned_share
    return (countable_unearned + countable_earned) * MONTHS_IN_YEAR
