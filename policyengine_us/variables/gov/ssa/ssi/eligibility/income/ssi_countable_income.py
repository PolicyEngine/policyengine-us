from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ssi_countable_income(Variable):
    value_type = float
    entity = Person
    label = "SSI countable income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382a#b"

    def formula(person, period, parameters):
        pre_reduction_earned_income = person(
            "ssi_marital_earned_income", period
        )
        blind_disabled_working_student_income = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        earned_income = max_(
            pre_reduction_earned_income
            - blind_disabled_working_student_income,
            0,
        )

        unearned_income = person("ssi_marital_unearned_income", period)
        parental_income_deemed_as_unearned_income = person(
            "ssi_unearned_income_deemed_from_ineligible_parent", period
        )

        personal_income = _apply_ssi_exclusions(
            earned_income,
            unearned_income + parental_income_deemed_as_unearned_income,
            parameters,
            period,
        )

        income_from_spouse = person(
            "ssi_income_deemed_from_ineligible_spouse", period
        )

        # Ensure the spouse whose income is deemed to their spouse loses their income.
        has_donated_income = (
            person.marital_unit.sum(income_from_spouse) > income_from_spouse
        )

        is_ssi_claimant = person("is_ssi_eligible_individual", period)

        return where(
            has_donated_income | ~is_ssi_claimant,
            0,
            personal_income + income_from_spouse,
        )
