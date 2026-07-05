from policyengine_us.model_api import *


class nd_ccap(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "North Dakota CCAP benefit amount"
    definition_period = MONTH
    defined_for = "nd_ccap_eligible"
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(spm_unit, period, parameters):
        # The benefit is the base subsidy (capped at billed expenses and net of
        # the co-payment) plus the additive QRIS step bonus and infant/toddler
        # bonus. The two bonuses are separate provider payments, so they are
        # not capped at the family's billed expenses and not reduced by the
        # co-payment (400-28-100-30).
        base_subsidy = spm_unit("nd_ccap_base_subsidy", period)
        qris_step_bonus = add(spm_unit, period, ["nd_ccap_qris_step_bonus"])
        infant_toddler_bonus = add(spm_unit, period, ["nd_ccap_infant_toddler_bonus"])
        return base_subsidy + qris_step_bonus + infant_toddler_bonus
