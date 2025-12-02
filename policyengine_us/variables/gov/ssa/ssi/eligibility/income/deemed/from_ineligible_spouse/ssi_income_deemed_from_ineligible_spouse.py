# policyengine_us/variables/gov/ssa/ssi/eligibility/income/deemed/from_ineligible_spouse/ssi_income_deemed_from_ineligible_spouse.py

from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class ssi_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI income (deemed from ineligible spouse)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"
    documentation = """
    Spousal deeming: 
      1) If leftover spouse income <= (coupleFBR - indivFBR), then 0 is deemed.
      2) Otherwise, spouse's deemed = (couple combined countable) - (individual alone countable).
         This yields 816 for 1986 Example 3 and 12000 for the 2025 test.
    """
    defined_for = "is_ssi_eligible_individual"
    unit = USD

    def formula(person, period, parameters):
        # 1. Check if spousal deeming applies (avoids duplicating threshold logic)
        deeming_applies = person("is_ssi_spousal_deeming_applies", period)

        # 2. If deeming applies, calculate deemed amount using "difference" approach:
        #    (couple combined countable) - (individual alone countable)

        # Get spouse's leftover income (post-child allocations)
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )

        # Get individual's own income
        individual_earned = person("ssi_earned_income", period)
        individual_unearned = person("ssi_unearned_income", period)

        # Calculate individual's countable income (alone)
        alone_countable = _apply_ssi_exclusions(
            individual_earned, individual_unearned, parameters, period
        )

        # Calculate couple's combined countable income
        couple_countable = _apply_ssi_exclusions(
            individual_earned + spouse_earned,
            individual_unearned + spouse_unearned,
            parameters,
            period,
        )

        # Deemed amount is the difference (only when deeming applies)
        deemed_amount = max_(0, couple_countable - alone_countable)
        return deeming_applies * deemed_amount
