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
    documentation = """
    Calculates how much income is deemed from an ineligible spouse to an SSI-eligible individual,
    under 20 CFR §416.1163. Steps:
      1. Subtract child allocations from spouse’s unearned, then earned.
      2. Check if leftover is <= the difference (couple FBR - individual FBR). If so, no deeming.
      3. If leftover is > the FBR difference, combine the spouse’s leftover with the individual's income
         and apply standard SSI income exclusions as if they were a couple. 
      4. The deemed amount is the difference between the "combined" countable income and the individual's
         countable income alone.
    """

    def formula(person, period, parameters):
        # Earned/unearned income from the ineligible spouse AFTER child allocations
        spousal_earned_income = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spousal_unearned_income = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )

        # If spouse leftover <= the difference between couple & individual FBR, no deeming
        ssi_params = parameters(period).gov.ssa.ssi.amount
        couple_annual = ssi_params.couple * MONTHS_IN_YEAR
        indiv_annual = ssi_params.individual * MONTHS_IN_YEAR
        fbr_diff = couple_annual - indiv_annual

        # Spouse leftover = spousal_earned + spousal_unearned (before exclusions).
        spouse_leftover = spousal_earned_income + spousal_unearned_income
        no_deeming = spouse_leftover <= fbr_diff

        # The individual's personal earned/unearned (already sets aside blind/disabled student exclusion)
        personal_earned = person("ssi_earned_income", period)
        personal_unearned = person("ssi_unearned_income", period)

        # Countable if we treat them as a couple: combine spouse + personal incomes, apply exclusions
        income_if_combined = _apply_ssi_exclusions(
            personal_earned + spousal_earned_income,
            personal_unearned + spousal_unearned_income,
            parameters,
            period,
        )

        # Countable if we treat the individual's income alone (still applying the same standard exclusions)
        income_if_not_combined = _apply_ssi_exclusions(
            personal_earned,
            personal_unearned,
            parameters,
            period,
        )

        # Deemed = difference if leftover > FBR differential; else 0
        deemed_income = income_if_combined - income_if_not_combined
        deemed_income = max_(0, deemed_income)

        # Only apply to the SSI-eligible person (and only if leftover > FBR diff).
        is_eligible = person("is_ssi_eligible_individual", period)
        return where(no_deeming | ~is_eligible, 0, deemed_income)
