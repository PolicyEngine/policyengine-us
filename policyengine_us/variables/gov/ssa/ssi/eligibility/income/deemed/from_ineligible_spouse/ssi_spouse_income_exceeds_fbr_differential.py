from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ssi_spouse_income_exceeds_fbr_differential(Variable):
    value_type = bool
    entity = Person
    label = "Spouse's income exceeds SSI FBR differential"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"
    documentation = """
    Determines if an ineligible spouse's income exceeds the SSI Federal Benefit Rate (FBR) differential.
    
    As specified in 20 CFR §416.1163(d)(1):
    "If the amount of your ineligible spouse's income ... does not exceed the difference between 
    the Federal benefit rate for an eligible couple and the Federal benefit rate for an eligible 
    individual, we do not deem any of that income to you."
    
    This threshold determines whether deeming from an ineligible spouse occurs.
    """

    def formula(person, period, parameters):
        # Check if the person is an eligible individual
        is_eligible = person("is_ssi_eligible_individual", period)
        
        # Check if the person has an ineligible spouse in their marital unit
        has_ineligible_spouse = person.marital_unit.any(
            person("is_ssi_ineligible_spouse", period)
        )

        # Get the spouse's income after allocations for ineligible children
        spousal_earned_income = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spousal_unearned_income = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )

        # Get SSI amount parameters and calculate the FBR differential threshold
        p = parameters(period).gov.ssa.ssi.amount
        fbr_differential = p.couple - p.individual

        # Apply exclusions to spouse's income to determine if it exceeds the differential
        # Convert annual income to monthly for the exclusions calculation
        monthly_earned = spousal_earned_income / MONTHS_IN_YEAR
        monthly_unearned = spousal_unearned_income / MONTHS_IN_YEAR
        
        # First apply general income exclusion to unearned income
        exclusions = parameters(period).gov.ssa.ssi.income.exclusions
        unearned_exclusion = min_(exclusions.general, monthly_unearned)
        countable_monthly_unearned = monthly_unearned - unearned_exclusion
        
        # Apply remaining general exclusion to earned income
        remaining_general_exclusion = exclusions.general - unearned_exclusion
        earned_exclusion = exclusions.earned + remaining_general_exclusion
        
        # Apply earned income exclusion and count 50% of the remainder
        countable_monthly_earned = max_(0, monthly_earned - earned_exclusion) * (1 - exclusions.earned_share)
        
        # Total countable monthly income
        spouse_countable_monthly_income = countable_monthly_unearned + countable_monthly_earned
        
        # Return True if spouse's income exceeds the differential threshold
        exceeds_threshold = spouse_countable_monthly_income > fbr_differential

        return is_eligible & has_ineligible_spouse & exceeds_threshold
