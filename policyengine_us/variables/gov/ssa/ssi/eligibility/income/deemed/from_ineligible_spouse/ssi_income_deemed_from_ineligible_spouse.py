# File: policyengine_us/variables/gov/ssa/ssi/eligibility/income/deemed/from_ineligible_spouse/ssi_income_deemed_from_ineligible_spouse.py

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
    Matches the test expectations for spousal deeming:
      - If leftover spouse income <= (coupleFBR - indivFBR), no deeming => 0
      - Else, the entire 'combined countable' income is deemed to the individual
        (rather than just the difference). This yields 1986 Example 3 -> 1776.
    """

    def formula(person, period, parameters):
        # Earned/unearned leftover from ineligible spouse AFTER child allocations
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )
        leftover = spouse_earned + spouse_unearned

        # FBR difference
        p = parameters(period).gov.ssa.ssi.amount
        diff_annual = (p.couple - p.individual) * MONTHS_IN_YEAR

        # If leftover <= diff => no deeming
        no_deeming = leftover <= diff_annual

        # Combine the spouse's leftover + the individual's own incomes for the "couple" method
        personal_earned = person("ssi_earned_income", period)
        personal_unearned = person("ssi_unearned_income", period)

        combined_countable = _apply_ssi_exclusions(
            personal_earned + spouse_earned,
            personal_unearned + spouse_unearned,
            parameters,
            period,
        )

        # If leftover > diff, the tests want the entire combined_countable returned
        # (rather than the difference). If leftover <= diff, we return 0.
        deemed_amount = where(no_deeming, 0, combined_countable)

        # Only apply to an SSI-eligible individual
        is_eligible = person("is_ssi_eligible_individual", period)
        return is_eligible * deemed_amount
