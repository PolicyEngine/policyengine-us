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
    documentation = """
    Calculates total countable income for SSI:
      - Earned (after ignoring blind/disabled student exclusion)
      - Unearned
      - Parental deemed if child
      - Spousal deemed if married to an ineligible spouse
      - Applies standard SSI exclusions.
    """

    def formula(person, period, parameters):
        # The individual's earned income, after the blind/disabled student exclusion
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

        # The individual's unearned + any unearned deemed from a parent
        # When both spouses are SSI eligible, ssi_marital_unearned_income and ssi_marital_earned_income
        # will already have attributed the combined earned/unearned income to each person in the
        # marital unit, so we don't need additional head/spouse checks here.
        # This occurs via the both_eligible check in those variables.
        unearned_income = person("ssi_marital_unearned_income", period)
        parent_deemed = person(
            "ssi_unearned_income_deemed_from_ineligible_parent", period
        )
        total_unearned = unearned_income + parent_deemed

        # Apply standard SSI exclusions to the individual's own income
        personal_countable = _apply_ssi_exclusions(
            earned_income,
            total_unearned,
            parameters,
            period,
        )

        # Check if both spouses are eligible
        both_eligible = person("ssi_marital_both_eligible", period)

        # Add spousal deemed income (only relevant when one spouse is ineligible)
        spousal_deemed = person(
            "ssi_income_deemed_from_ineligible_spouse", period
        )

        # Check if person is eligible (either as individual OR as eligible spouse)
        is_eligible_individual = person("is_ssi_eligible_individual", period)
        is_eligible_spouse = person("is_ssi_eligible_spouse", period)
        is_eligible = is_eligible_individual | is_eligible_spouse

        # Calculate final countable income
        return where(
            ~is_eligible,
            0,
            where(
                both_eligible,
                personal_countable / 2,  # Each eligible spouse gets half
                personal_countable
                + spousal_deemed,  # Single or with ineligible spouse
            ),
        )
