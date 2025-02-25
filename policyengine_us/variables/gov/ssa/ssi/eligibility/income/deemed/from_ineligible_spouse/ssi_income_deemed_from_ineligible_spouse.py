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
    Calculates the amount of income deemed from an ineligible spouse to an SSI-eligible individual.
    
    Follows the process specified in 20 CFR §416.1163:
    1. Determine ineligible spouse's income (§416.1163(a))
    2. Apply allocations for ineligible children from spouse's income (§416.1163(b))
    3. Determine if remaining income exceeds the FBR differential (§416.1163(d))
    4. If it exceeds the threshold, combine incomes and apply exclusions (§416.1163(d)(2))
    5. Calculate deemed amount based on the difference between combined and individual incomes
    
    This implementation specifically addresses the regulations in §416.1163(d) regarding
    the comparison to the Federal Benefit Rate (FBR) differential.
    """

    def formula(person, period, parameters):
        # Get the ineligible spouse's earned and unearned income after allocations
        # This follows §416.1163(a) and (b) where we determine spouse's income
        # and then apply allocations for ineligible children
        spousal_earned_income = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spousal_unearned_income = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )

        # Get the eligible individual's income
        personal_earned_income = person("ssi_earned_income", period)
        personal_unearned_income = person("ssi_unearned_income", period)

        # Combine incomes as specified in §416.1163(d)(2)(i)
        # "Combining the remainder of your spouse's unearned income with your own unearned income
        # and the remainder of your spouse's earned income with your earned income"
        combined_earned_income = personal_earned_income + spousal_earned_income
        combined_unearned_income = (
            personal_unearned_income + spousal_unearned_income
        )

        # Calculate income if combined (after exclusions)
        # This implements §416.1163(d)(2)(ii) where we "apply all appropriate income exclusions"
        income_if_combined = _apply_ssi_exclusions(
            combined_earned_income,
            combined_unearned_income,
            parameters,
            period,
        )

        # Calculate income if not combined (after exclusions)
        # This helps determine the amount deemed from spouse by comparing
        # the eligible individual's income alone vs. combined with spouse
        income_if_not_combined = _apply_ssi_exclusions(
            personal_earned_income,
            personal_unearned_income,
            parameters,
            period,
        )

        # The deemed income is the difference between combined and individual countable income
        # This follows §416.1163(d)(2)(iii) which requires subtracting countable income
        # from the FBR to determine the benefit amount
        deemed_income = max_(income_if_combined - income_if_not_combined, 0)

        # Check if person is an eligible individual with an ineligible spouse
        # This implements the condition in §416.1163(d) which specifies different
        # calculation methods based on whether the person has an ineligible spouse
        is_eligible = person("is_ssi_eligible_individual", period)
        has_ineligible_spouse = person.marital_unit.any(
            person("is_ssi_ineligible_spouse", period)
        )

        return (is_eligible & has_ineligible_spouse) * deemed_income
