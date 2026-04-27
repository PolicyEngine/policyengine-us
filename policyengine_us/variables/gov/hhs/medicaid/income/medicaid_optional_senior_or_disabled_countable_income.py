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


class medicaid_optional_senior_or_disabled_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Countable income for Medicaid's optional senior or disabled pathway"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://www.kff.org/medicaid/medicaid-financial-eligibility-for-seniors-and-people-with-disabilities-findings-from-a-50-state-survey/",
    )

    def formula(person, period, parameters):
        pre_reduction_earned_income = person("ssi_marital_earned_income", period)
        blind_disabled_working_student_income = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        earned_income = max_(
            pre_reduction_earned_income
            - blind_disabled_working_student_income,
            0,
        )

        unearned_income = person("ssi_marital_unearned_income", period)
        parent_deemed = person(
            "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
            period,
        )
        total_unearned = unearned_income + parent_deemed

        both_eligible = person("ssi_marital_both_eligible", period)
        state = person.household("state_code_str", period)
        p = (
            parameters(period)
            .gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.disregard
        )
        income_disregard = where(
            both_eligible,
            p.couple[state],
            p.individual[state],
        )
        personal_countable = where(
            state == "CT",
            _apply_ct_husky_c_exclusions(
                earned_income,
                total_unearned,
                income_disregard,
                parameters,
                period,
            ),
            _apply_ssi_exclusions(
                earned_income,
                total_unearned,
                parameters,
                period,
                general_exclusion=income_disregard,
            ),
        )

        spousal_deemed = person(
            "medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse",
            period,
        )
        is_eligible_individual = person("is_ssi_eligible_individual", period)
        is_eligible_spouse = person("is_ssi_eligible_spouse", period)
        is_eligible = is_eligible_individual | is_eligible_spouse

        return where(
            ~is_eligible,
            0,
            where(
                both_eligible,
                personal_countable / 2,
                personal_countable + spousal_deemed,
            ),
        )
