from policyengine_us.model_api import *


class mn_mfip(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = "mn_mfip_eligible"

    def formula(spm_unit, period, parameters):
        payment_standard = spm_unit("mn_mfip_payment_standard", period)
        family_wage_level = spm_unit("mn_mfip_family_wage_level", period)
        countable_earned = spm_unit("mn_mfip_countable_earned_income", period)
        countable_unearned = spm_unit(
            "mn_mfip_countable_unearned_income", period
        )
        earned_based_benefit = min_(
            family_wage_level - countable_earned, payment_standard
        )
        return max_(earned_based_benefit - countable_unearned, 0)
