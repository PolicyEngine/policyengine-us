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


def _apply_mo_mhabd_exclusions(
    earned_income: ArrayLike,
    unearned_income: ArrayLike,
    income_disregard: ArrayLike,
    parameters: ParameterNode,
    period: Period,
) -> ArrayLike:
    # Missouri MHABD budgets in the order of DSS Manual § 0805.015.00:
    # deduct the $65-plus-one-half earned income exemption from gross
    # earned income (§ 0805.015.25), add unearned income, subtract the
    # standard exemption, then round the remaining income down to the
    # nearest whole dollar (§ 0805.015.40). Unlike SSI, no unused portion
    # of the standard exemption shifts to earned income before the
    # 50-percent exclusion.
    p = parameters(period).gov.ssa.ssi.income.exclusions
    earned_monthly = earned_income / MONTHS_IN_YEAR
    unearned_monthly = unearned_income / MONTHS_IN_YEAR

    adjusted_earned = max_(earned_monthly - p.earned, 0) * (1.0 - p.earned_share)
    adjusted = max_(adjusted_earned + unearned_monthly - income_disregard, 0)
    return np.floor(adjusted) * MONTHS_IN_YEAR


def _apply_medicaid_optional_senior_or_disabled_exclusions(
    earned_income: ArrayLike,
    unearned_income: ArrayLike,
    state: ArrayLike,
    income_disregard: ArrayLike,
    parameters: ParameterNode,
    period: Period,
) -> ArrayLike:
    return select(
        [state == "CT", state == "MO"],
        [
            _apply_ct_husky_c_exclusions(
                earned_income,
                unearned_income,
                income_disregard,
                parameters,
                period,
            ),
            _apply_mo_mhabd_exclusions(
                earned_income,
                unearned_income,
                income_disregard,
                parameters,
                period,
            ),
        ],
        default=_apply_ssi_exclusions(
            earned_income,
            unearned_income,
            parameters,
            period,
            general_exclusion=income_disregard,
        ),
    )
