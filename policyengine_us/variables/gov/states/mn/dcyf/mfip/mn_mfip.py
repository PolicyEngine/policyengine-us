from policyengine_us.model_api import *


class mn_mfip(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G.16"
    defined_for = "mn_mfip_eligible"

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 142G.16, Subd. 2 (benefit calculation):
        # (a) FWL - countable earned = X, cap at transitional standard
        # (d) X - unearned = final benefit
        # Note: Dependent care deduction does NOT apply to benefit calculation
        transitional_standard = spm_unit(
            "mn_mfip_transitional_standard", period
        )
        family_wage_level = spm_unit("mn_mfip_family_wage_level", period)
        countable_earned = spm_unit("mn_mfip_countable_earned_income", period)
        countable_unearned = spm_unit(
            "mn_mfip_countable_unearned_income", period
        )
        # Step 1: Subtract countable earned from FWL, floor at 0
        fwl_minus_earned = max_(family_wage_level - countable_earned, 0)
        # Step 2: Cap at transitional standard
        earned_based_benefit = min_(fwl_minus_earned, transitional_standard)
        # Step 3: Subtract countable unearned income, floor at zero
        return max_(earned_based_benefit - countable_unearned, 0)
