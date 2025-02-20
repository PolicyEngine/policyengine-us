from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ssi_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI income (deemed from ineligible spouse)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"

    def formula(person, period, parameters):
        # Get the ineligible spouse's earned income
        spousal_earned_income = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spousal_unearned_income = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )

        # Get the eligible individual's income
        personal_earned_income = person("ssi_earned_income", period)
        personal_unearned_income = person("ssi_unearned_income", period)

        # Apply earned income exclusions to combined income
        combined_earned_income = personal_earned_income + spousal_earned_income
        combined_unearned_income = (
            personal_unearned_income + spousal_unearned_income
        )

        # Calculate income if combined (after exclusions)
        income_if_combined = _apply_ssi_exclusions(
            combined_earned_income,
            combined_unearned_income,
            parameters,
            period,
        )

        # Calculate income if not combined (after exclusions)
        income_if_not_combined = _apply_ssi_exclusions(
            personal_earned_income,
            personal_unearned_income,
            parameters,
            period,
        )

        # The deemed income is the difference between combined and individual
        deemed_income = max_(income_if_combined - income_if_not_combined, 0)

        # Check if person is an eligible individual with an ineligible spouse
        is_eligible = person("is_ssi_eligible_individual", period)
        has_ineligible_spouse = person.marital_unit.any(
            person("is_ssi_ineligible_spouse", period)
        )

        return (is_eligible & has_ineligible_spouse) * deemed_income
