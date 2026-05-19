from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


def _apply_ct_husky_c_exclusions(
    earned_income: ArrayLike,
    unearned_income: ArrayLike,
    income_disregard: ArrayLike,
    parameters: ParameterNode,
    period: Period,
) -> ArrayLike:
    p = parameters(period).gov.ssa.ssi.income.exclusions
    earned_monthly = earned_income / MONTHS_IN_YEAR
    unearned_monthly = unearned_income / MONTHS_IN_YEAR

    return (
        max_(unearned_monthly - income_disregard, 0)
        + max_(earned_monthly - p.earned, 0) * (1.0 - p.earned_share)
    ) * MONTHS_IN_YEAR


def _apply_medicaid_optional_senior_or_disabled_exclusions(
    earned_income: ArrayLike,
    unearned_income: ArrayLike,
    state: ArrayLike,
    income_disregard: ArrayLike,
    parameters: ParameterNode,
    period: Period,
) -> ArrayLike:
    return where(
        state == "CT",
        _apply_ct_husky_c_exclusions(
            earned_income,
            unearned_income,
            income_disregard,
            parameters,
            period,
        ),
        _apply_ssi_exclusions(
            earned_income,
            unearned_income,
            parameters,
            period,
            general_exclusion=income_disregard,
        ),
    )
