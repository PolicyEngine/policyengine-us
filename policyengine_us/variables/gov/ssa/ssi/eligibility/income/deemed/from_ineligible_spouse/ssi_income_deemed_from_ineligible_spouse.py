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
        # 1. Sum leftover spouse earned/unearned (post-child allocations).
        spouse_earned = person(
            "ssi_earned_income_deemed_from_ineligible_spouse", period
        )
        spouse_unearned = person(
            "ssi_unearned_income_deemed_from_ineligible_spouse", period
        )
        leftover_spouse = spouse_earned + spouse_unearned

        # 2. Compare leftover to FBR difference
        p = parameters(period).gov.ssa.ssi.amount
        diff = (p.couple - p.individual) * MONTHS_IN_YEAR
        if_leftover_exceeds = leftover_spouse > diff

        # 3. If leftover <= diff => no deeming
        #    If leftover > diff => difference of incomes approach
        #    (couple combined) - (individual alone).
        #   (a) individual's own income
        indiv_earned = person("ssi_earned_income", period)
        indiv_unearned = person("ssi_unearned_income", period)
        alone_countable = _apply_ssi_exclusions(
            indiv_earned, indiv_unearned, parameters, period
        )

        #   (b) couple combined income
        couple_countable = _apply_ssi_exclusions(
            indiv_earned + spouse_earned,
            indiv_unearned + spouse_unearned,
            parameters,
            period,
        )

        deemed_if_exceeds = max_(0, couple_countable - alone_countable)
        return if_leftover_exceeds * deemed_if_exceeds
