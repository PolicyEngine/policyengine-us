from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)


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
            pre_reduction_earned_income - blind_disabled_working_student_income,
            0,
        )

        total_unearned_income = add(
            person,
            period,
            [
                "ssi_marital_unearned_income",
                "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
            ],
        )

        couple_computation = person("ssi_couple_computation_applies", period)
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income.disregard
        income_disregard = where(
            couple_computation,
            p.couple[state],
            p.individual[state],
        )
        personal_countable = _apply_medicaid_optional_senior_or_disabled_exclusions(
            earned_income,
            total_unearned_income,
            state,
            income_disregard,
            parameters,
            period,
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
                couple_computation,
                personal_countable / 2,
                personal_countable + spousal_deemed,
            ),
        )
